"""Tab 1 - desk tools: market what-if, DV01 family, swap book & hedging, FRA / futures convexity."""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import qd_rates as R
import qd_desk as K
import qd_ui as ui


def _ins(key):
    return [R.Instrument(*k[:3], label=k[3]) for k in key]


@st.cache_data(show_spinner=False)
def _krd(key, freq, method, N, fixed, Tsw, receive, bp):
    c = R.build_curve(_ins(key), freq, method)
    f = lambda cu: R.swap_pv(cu, N, fixed, Tsw, freq, receive)
    return R.key_rate_dv01(c, f, bp), R.parallel_dv01(c, f, bp)


@st.cache_data(show_spinner=False)
def _ladder(key, freq, method, N, fixed, Tsw, receive):
    c = R.build_curve(_ins(key), freq, method)
    f = lambda cu: R.swap_pv(cu, N, fixed, Tsw, freq, receive)
    lad, d, g = K.pv_ladder(c, f, [-100, -50, -25, 0, 25, 50, 100])
    return lad, d, g


def _curve(key, freq, method):
    from tab_curve import build_cached      # cached bootstrap shared with the Curve tab (imported lazily: no import cycle)
    return build_cached(key, freq, method)


@st.cache_data(show_spinner=False)
def _book_cached(key, freq, method, trades, hedge_t, ridge):
    c = _curve(key, freq, method)
    tr = [K.Trade(*t) for t in trades]
    bs = K.book_summary(c, tr, freq)
    if not hedge_t:
        return bs, None, None, None
    H = K.hedge_matrix(c, list(hedge_t), freq, bs["nodes"])
    x, res = K.solve_hedge(bs["zero_buckets"], H, ridge)
    hedges = [K.Trade(1 if v >= 0 else -1, abs(float(v)), float(t_), c.par_rate(float(t_), freq), 0.0) for v, t_ in zip(x, hedge_t) if abs(v) > 1.0]
    after = K.book_summary(c, tr + hedges, freq) if hedges else bs
    return bs, x, after, hedges


def render(T, th, curve, key, freq, method, ins, swap, can_apply):
    ui.section(T("dk_title"), T("dk_sub"))
    t1, t2, t3, t4 = st.tabs([T("dk_t_whatif"), T("dk_t_ladder"), T("dk_t_book"), T("dk_t_fra")])
    with t1:
        _whatif(T, th, curve, freq, ins, swap, can_apply)
    with t2:
        _ladder_tab(T, th, curve, key, freq, method, swap)
    with t3:
        _book(T, th, curve, key, freq, method, swap)
    with t4:
        _fra(T, th, curve, freq)
    with st.expander(T("dk_refs")):
        st.markdown(T("dk_refs_body").replace("$", "\\$"))


# ============================================================================================ what-if
@st.fragment
def _whatif(T, th, curve, freq, ins, swap, can_apply):
    tenors = [i.tenor for i in curve.instruments]
    c = st.columns([1, 1, 1, 1.2])
    lvl = c[0].slider(T("dk_level"), -150, 150, 0, 1, key="dk_lvl", help=T("dk_level_help"))
    slp = c[1].slider(T("dk_slope"), -100, 100, 0, 1, key="dk_slp", help=T("dk_slope_help"))
    crv = c[2].slider(T("dk_curv"), -75, 75, 0, 1, key="dk_crv", help=T("dk_curv_help"))
    show = c[3].segmented_control(T("view"), ["zero", "par", "fwd"], default="zero", key="dk_show", format_func=lambda x: T("dk_s_" + x), label_visibility="collapsed") or "zero"
    ov = np.zeros(len(tenors))
    with st.expander(T("dk_pillar")):
        base_df = pd.DataFrame({"label": [i.label for i in curve.instruments], "base": [i.quote * 100 for i in curve.instruments], "bump_bp": 0.0})
        ed = st.data_editor(base_df, hide_index=True, width="stretch", key=f"dk_ov_{len(tenors)}", disabled=["label", "base"],
                            column_config={"label": st.column_config.TextColumn(T("instr")), "base": st.column_config.NumberColumn(T("rate_pct"), format="%.4f"),
                                           "bump_bp": st.column_config.NumberColumn(T("dk_bump"), format="%.1f", min_value=-500.0, max_value=500.0)})
        ov = ed["bump_bp"].fillna(0.0).to_numpy(float)
    bumps = K.factor_bumps(tenors, lvl, slp, crv) + ov
    idle = not np.any(np.abs(bumps) > 1e-12)
    if idle:
        ui.note(T("dk_whatif_idle"))
    try:
        new = curve if idle else R.shock(curve, bumps)
    except ValueError as e:
        ui.note(T("build_err", e=str(e)), "neg")
        return
    tt = np.linspace(0.05, curve.tmax, 300)
    cmp_ = K.compare_curves(curve, new, [0.5, 1, 2, 3, 5, 7, 10, 20, 30] if curve.tmax >= 30 else [x for x in (0.5, 1, 2, 3, 5, 7, 10, 20) if x <= curve.tmax])
    pv0 = R.swap_pv(curve, swap["N"], swap["K"], swap["T"], freq, swap["rec"])
    pv1 = R.swap_pv(new, swap["N"], swap["K"], swap["T"], freq, swap["rec"])
    s0, s1 = R.curve_stats(curve), R.curve_stats(new)
    d = lambda k: (s1[k] - s0[k]) * (1e4 if k in ("z2", "z10", "f5y5y") else 1.0)
    ui.kpi_strip(th, [
        {"label": T("dk_d2"), "value": d("z2"), "dec": 1, "suffix": " bp", "sub": T("cc")},
        {"label": T("dk_d10"), "value": d("z10"), "dec": 1, "suffix": " bp", "sub": T("cc")},
        {"label": "Δ 2s10s", "value": d("s2s10s"), "dec": 1, "suffix": " bp", "sub": T("shape_" + s1["shape"])},
        {"label": "Δ 5y5y", "value": None if np.isnan(d("f5y5y")) else d("f5y5y"), "dec": 1, "suffix": " bp", "sub": T("annual")},
        {"label": T("dk_swap_pnl"), "value": pv1 - pv0, "dec": 0, "prefix": "$", "tone": "pos" if pv1 - pv0 >= 0 else "neg", "sub": f"{T('side_rec') if swap['rec'] else T('side_pay')} {swap['T']:g}Y"},
    ])
    a, b = st.columns([1.6, 1], gap="large")
    fig = go.Figure()
    if show == "zero":
        f0, f1, nm = curve.zero(tt, "cc") * 100, new.zero(tt, "cc") * 100, T("l_zero")
    elif show == "par":
        f0 = np.array([curve.par_rate(x, freq) if x >= 1 / freq else np.nan for x in tt]) * 100
        f1 = np.array([new.par_rate(x, freq) if x >= 1 / freq else np.nan for x in tt]) * 100
        nm = T("l_par")
    else:
        f0, f1, nm = curve.inst_forward(tt) * 100, new.inst_forward(tt) * 100, T("l_fwd")
    fig.add_trace(go.Scatter(x=tt, y=f0, name=T("dk_base"), line=dict(color=th["accent"], width=3), hovertemplate="%{y:.3f}%"))
    fig.add_trace(go.Scatter(x=tt, y=f1, name=T("dk_shocked"), line=dict(color=th["c"][4], width=2.4, dash="dash"), hovertemplate="%{y:.3f}%"))
    fig.update_layout(**ui.plotly_layout(th, 330, xaxis_title=T("maturity"), yaxis_title=nm + " (%)"))
    a.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    cols = {"d_zero": T("dk_s_zero"), "d_par": T("dk_s_par"), "d_fwd": T("dk_s_fwd")}
    fb = go.Figure()
    for k, col in zip(cols, (th["accent"], th["c"][1], th["c"][2])):
        fb.add_trace(go.Bar(x=[f"{t:g}Y" for t in cmp_["t"]], y=cmp_[k], name=cols[k], marker=dict(color=col, cornerradius=3), hovertemplate="%{y:+.1f} bp"))
    fb.update_layout(**ui.plotly_layout(th, 330, barmode="group", yaxis_title="Δ bp", title=dict(text=T("dk_delta_title"), font=dict(size=14))))
    b.plotly_chart(fb, width="stretch", config={"displayModeBar": False})
    bc = st.columns([1, 3])
    if idle:
        return
    if can_apply:
        if bc[0].button(T("dk_apply"), type="primary", width="stretch", key="dk_apply_btn"):
            st.session_state["_q_df"] = pd.DataFrame({"label": [i.label for i in curve.instruments], "years": tenors, "kind": [i.kind for i in curve.instruments],
                                                      "rate": [(i.quote + bumps[k] / 1e4) * 100 for k, i in enumerate(curve.instruments)]})
            st.session_state["_q_ver"] = st.session_state.get("_q_ver", 0) + 1
            for k_ in ("dk_lvl", "dk_slp", "dk_crv"):
                st.session_state[k_] = 0
            st.rerun()
        bc[1].caption(T("dk_apply_help"))
    else:
        bc[1].caption(T("dk_apply_off"))


# ============================================================================================ DV01 family
@st.fragment
def _ladder_tab(T, th, curve, key, freq, method, swap):
    c = st.columns([1.3, 1.1, 2])
    typ = c[0].segmented_control(T("dk_dv_type"), ["par", "zero", "fwd"], default="par", key="dk_dv_type", format_func=lambda x: T("dk_dv_" + x)) or "par"
    bp = c[1].select_slider(T("dk_bump_size"), [0.1, 0.5, 1.0, 5.0, 10.0], 1.0, key="dk_bump_size", format_func=lambda x: f"{x:g} bp")
    c[2].caption(T("dk_dv_help_" + typ))
    N, Kf, Tsw, rec = swap["N"], swap["K"], swap["T"], swap["rec"]
    f = lambda cu: R.swap_pv(cu, N, Kf, Tsw, freq, rec)
    pv = f(curve)
    zdv = K.zero_dv01(curve, f, bp)
    gam = K.gamma_zero(curve, f, bp)
    pv01 = K.fixed_leg_pv01(curve, N, Tsw, freq) * (1 if rec else -1)
    krd, pdv = _krd(key, freq, method, float(N), float(Kf), float(Tsw), bool(rec), float(bp))
    ui.kpi_strip(th, [
        {"label": T("dk_k_par"), "value": pdv, "dec": 0, "prefix": "$", "sub": T("dk_k_par_s")},
        {"label": T("dk_k_zero"), "value": zdv, "dec": 0, "prefix": "$", "sub": T("dk_k_zero_s")},
        {"label": "PV01 " + T("dk_annuity"), "value": pv01, "dec": 0, "prefix": "$", "sub": T("dk_pv01_s")},
        {"label": T("dk_gamma"), "value": gam / bp ** 2, "dec": 2, "prefix": "$", "sub": T("dk_gamma_s"), "tone": "pos" if gam >= 0 else "neg"},
        {"label": T("dk_dur"), "value": abs(zdv) * 1e4 / max(abs(N), 1) if N else None, "dec": 2, "sub": T("dk_dur_s")},
    ])
    if typ == "par":
        labels = [i.label for i in curve.instruments]
        vals = krd
    elif typ == "zero":
        nodes = [i.tenor for i in curve.instruments]
        labels = [i.label for i in curve.instruments]
        vals = K.zero_bucket_dv01(curve, f, nodes, bp)
    else:
        edges = [e for e in (0, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30) if e < curve.tmax - 1e-9]
        labels = [f"{a:g}–{b:g}Y" for a, b in zip(edges, edges[1:] + [curve.tmax])]
        vals = K.fwd_bucket_dv01(curve, f, edges, bp)
    g1, g2 = st.columns(2, gap="large")
    fig = go.Figure(go.Bar(x=labels, y=vals, marker=dict(color=[th["pos"] if v >= 0 else th["neg"] for v in vals], cornerradius=4), hovertemplate="%{x}: $%{y:,.0f}/bp<extra></extra>"))
    fig.update_layout(**ui.plotly_layout(th, 320, showlegend=False, hovermode="closest", title=dict(text=T("dk_dv_" + typ) + " · " + T("dk_sum", s=f"{np.nansum(vals):,.0f}"), font=dict(size=14))))
    g1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    lad, d, g = _ladder(key, freq, method, float(N), float(Kf), float(Tsw), bool(rec))
    fl = go.Figure()
    fl.add_trace(go.Scatter(x=lad["shock_bp"], y=lad["full"], name=T("dk_full"), line=dict(color=th["accent"], width=3), hovertemplate="$%{y:,.0f}"))
    fl.add_trace(go.Scatter(x=lad["shock_bp"], y=lad["delta"], name=T("dk_delta_only"), line=dict(color=th["c"][2], width=1.8, dash="dash"), hovertemplate="$%{y:,.0f}"))
    fl.add_trace(go.Scatter(x=lad["shock_bp"], y=lad["delta_gamma"], name=T("dk_delta_gamma"), line=dict(color=th["c"][1], width=1.8, dash="dot"), hovertemplate="$%{y:,.0f}"))
    fl.add_hline(y=0, line=dict(color=th["grid"], width=1))
    fl.update_layout(**ui.plotly_layout(th, 320, xaxis_title=T("dk_shock_bp"), yaxis_title="P&L $", title=dict(text=T("dk_ladder_title"), font=dict(size=14))))
    g2.plotly_chart(fl, width="stretch", config={"displayModeBar": False})
    tb = pd.DataFrame({T("dk_bucket"): labels, "DV01 $": np.round(np.asarray(vals, float), 2) + 0.0})
    cc = st.columns([3, 1])
    cc[0].dataframe(tb.style.format({"DV01 $": "{:,.1f}"}), hide_index=True, width="stretch", height=min(36 * (len(tb) + 1) + 3, 300))
    cc[1].download_button(T("dk_csv"), tb.to_csv(index=False).encode(), "dv01_buckets.csv", "text/csv")
    ui.note(T("dk_ladder_note", g=f"{lad.loc[lad.shock_bp == 100, 'full'].iloc[0]:+,.0f}", dg=f"{lad.loc[lad.shock_bp == 100, 'delta_gamma'].iloc[0]:+,.0f}"))


# ============================================================================================ book & hedge
@st.fragment
def _book(T, th, curve, key, freq, method, swap):
    n_ins = len(curve.instruments)
    if "dk_book" not in st.session_state:
        st.session_state["dk_book"] = pd.DataFrame({"side": ["rec" if swap["rec"] else "pay"], "notional": [float(swap["N"])], "tenor": [float(swap["T"])],
                                                    "fixed": [float(swap["K"] * 100)], "start": [0.0]})
        st.session_state["dk_book_ver"] = 0
    top = st.columns([3, 1])
    top[0].markdown(f"**{T('dk_book_title')}**")
    if top[1].button(T("dk_book_reset"), width="stretch", key="dk_book_rst"):
        del st.session_state["dk_book"]
        st.rerun(scope="fragment")
    bk = st.data_editor(st.session_state["dk_book"], hide_index=True, width="stretch", num_rows="dynamic", key=f"dk_book_ed{st.session_state.get('dk_book_ver', 0)}",
                        column_config={"side": st.column_config.SelectboxColumn(T("side"), options=["rec", "pay"], required=True),
                                       "notional": st.column_config.NumberColumn(T("notional"), min_value=1.0, format="%.0f"),
                                       "tenor": st.column_config.NumberColumn(T("swap_T"), min_value=0.5, max_value=float(curve.tmax), format="%.2f"),
                                       "fixed": st.column_config.NumberColumn(T("fixed_rate"), help=T("dk_fixed_blank"), format="%.4f"),
                                       "start": st.column_config.NumberColumn(T("dk_start"), min_value=0.0, max_value=float(curve.tmax), format="%.2f")})
    trades = []
    for r in bk.dropna(subset=["side", "notional", "tenor"]).itertuples():
        s0 = 0.0 if r.start != r.start else float(r.start)
        if r.tenor + s0 > curve.tmax + 1e-9:
            continue
        fx = curve.par_rate(float(r.tenor), freq, s0) if (r.fixed != r.fixed or r.fixed is None) else float(r.fixed) / 100
        trades.append(K.Trade(1 if r.side == "rec" else -1, float(r.notional), float(r.tenor), fx, s0))
    if not trades:
        ui.note(T("dk_book_empty"), "warn")
        return
    tt_ = tuple((t.side, t.notional, t.tenor, t.fixed, t.start, t.label) for t in trades)
    bs = _book_cached(key, freq, method, tt_, (), 0.0)[0]
    ui.kpi_strip(th, [
        {"label": T("k_pv"), "value": bs["pv"], "dec": 0, "prefix": "$", "tone": "pos" if bs["pv"] >= 0 else "neg", "sub": f"{len(trades)} " + T("dk_trades")},
        {"label": T("dk_k_par"), "value": bs["par_dv01"], "dec": 0, "prefix": "$", "sub": T("dk_k_par_s")},
        {"label": T("dk_k_zero"), "value": bs["zero_dv01"], "dec": 0, "prefix": "$", "sub": T("dk_k_zero_s")},
        {"label": T("dk_gamma"), "value": bs["gamma"], "dec": 1, "prefix": "$", "sub": T("dk_gamma_s"), "tone": "pos" if bs["gamma"] >= 0 else "neg"},
    ])
    nodes = bs["nodes"]
    labels = [i.label for i in curve.instruments]
    # ---------------- hedge
    st.markdown(f"**{T('dk_hedge_title')}**")
    cands = [t_ for t_ in (0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30) if t_ <= curve.tmax + 1e-9]
    hc = st.columns([2, 1.2, 1.2])
    hedge_t = hc[0].multiselect(T("dk_hedge_with"), cands, [t_ for t_ in (2, 5, 10, 30) if t_ in cands], key="dk_hedge_t", format_func=lambda x: f"{x:g}Y")
    ridge = hc[1].select_slider(T("dk_ridge"), [0.0, 1e-6, 1e-4, 1e-2], 0.0, key="dk_ridge", format_func=lambda x: T("dk_ridge_off") if x == 0 else f"{x:.0e}", help=T("dk_ridge_help"))
    if not hedge_t:
        ui.note(T("dk_hedge_pick"), "warn")
        return
    bs, x, after, hedges = _book_cached(key, freq, method, tt_, tuple(hedge_t), float(ridge))
    red = 1 - np.linalg.norm(after["zero_buckets"]) / max(np.linalg.norm(bs["zero_buckets"]), 1e-12)
    ui.kpi_strip(th, [
        {"label": T("dk_res_zero"), "value": after["zero_dv01"], "dec": 0, "prefix": "$", "sub": T("dk_after")},
        {"label": T("dk_res_par"), "value": after["par_dv01"], "dec": 0, "prefix": "$", "sub": T("dk_after_par")},
        {"label": T("dk_res_norm"), "value": red * 100, "dec": 1, "suffix": "%", "sub": T("dk_res_norm_s"), "tone": "pos"},
        {"label": T("dk_gross"), "value": float(np.sum(np.abs(x))), "dec": 0, "prefix": "$", "sub": T("dk_gross_s")},
    ])
    g1, g2 = st.columns([1.5, 1], gap="large")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=bs["zero_buckets"], name=T("dk_before"), marker=dict(color=th["c"][2], cornerradius=3), hovertemplate="%{y:,.0f}"))
    fig.add_trace(go.Bar(x=labels, y=after["zero_buckets"], name=T("dk_after"), marker=dict(color=th["accent"], cornerradius=3), hovertemplate="%{y:,.0f}"))
    fig.update_layout(**ui.plotly_layout(th, 320, barmode="group", yaxis_title="DV01 $/bp", title=dict(text=T("dk_hedge_chart"), font=dict(size=14))))
    g1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    ht = pd.DataFrame({T("dk_instr"): [f"{t_:g}Y {T('l_par')}" for t_ in hedge_t], T("dk_notional_signed"): x,
                       T("dk_action"): [T("side_rec") if v >= 0 else T("side_pay") for v in x]})
    g2.dataframe(ht.style.format({T("dk_notional_signed"): "{:+,.0f}"}), hide_index=True, width="stretch")
    g2.caption(T("dk_hedge_note"))
    # ---------------- DV01-neutral curve trades
    st.markdown(f"**{T('dk_ct_title')}**")
    ct = st.columns([1.2, 1, 1, 1.2])
    kind = ct[0].segmented_control(T("dk_ct_kind"), ["steep", "flat", "fly"], default="steep", key="dk_ct_kind", format_func=lambda x: T("dk_ct_" + x)) or "steep"
    opts = [t_ for t_ in cands if t_ >= 1]
    if kind == "fly":
        a_ = ct[1].selectbox(T("dk_wing1"), opts, index=min(2, len(opts) - 1), key="dk_w1", format_func=lambda x: f"{x:g}Y")
        b_ = ct[2].selectbox(T("dk_belly"), opts, index=min(4, len(opts) - 1), key="dk_bl", format_func=lambda x: f"{x:g}Y")
        c_ = ct[3].selectbox(T("dk_wing2"), opts, index=min(6, len(opts) - 1), key="dk_w2", format_func=lambda x: f"{x:g}Y")
    else:
        a_ = ct[1].selectbox(T("dk_short_leg"), opts, index=min(2, len(opts) - 1), key="dk_sl", format_func=lambda x: f"{x:g}Y")
        c_ = ct[2].selectbox(T("dk_long_leg"), opts, index=min(6, len(opts) - 1), key="dk_ll", format_func=lambda x: f"{x:g}Y")
        b_ = None
    nl = st.number_input(T("dk_ct_notional"), 1e5, 1e10, 1e7, 1e6, format="%.0f", key="dk_ct_n")
    if (kind != "fly" and a_ >= c_) or (kind == "fly" and not (a_ < b_ < c_)):
        ui.note(T("dk_ct_order"), "warn")
    else:
        tenors_all = [i.tenor for i in curve.instruments]
        if kind == "fly":
            fl = K.dv01_neutral_fly(curve, a_, b_, c_, nl, freq)
            legs = [(-1, fl["N1"], a_), (1, fl["N2"], b_), (-1, fl["N3"], c_)]
            moves = {"belly": [-25, -10, 10, 25]}
        else:
            sp = K.dv01_neutral_spread(curve, a_, c_, nl, freq)
            # steepener: receive the short leg, pay the long leg ; flattener: the reverse
            sg = 1 if kind == "steep" else -1
            legs = [(sg, sp["N_short"], a_), (-sg, sp["N_long"], c_)]
        book = [K.Trade(s_, n_, t_, curve.par_rate(t_, freq), 0.0) for s_, n_, t_ in legs]
        f = lambda cu: K.book_pv(cu, book, freq)
        scen_rows = []
        for mv in (-25, -10, 10, 25):
            if kind == "fly":
                bmp = R.scenario_bumps(tenors_all, 0, 0, mv, belly_t=b_, belly_w=max((c_ - a_) / 3, 1.0))
            else:
                bmp = R.scenario_bumps(tenors_all, -mv / 2, mv / 2, 0)
            scen_rows.append((mv, R._pv_shocked(curve, f, bmp) - f(curve)))
        ctd = pd.DataFrame({T("dk_instr"): [f"{t_:g}Y" for _, _, t_ in legs], T("dk_action"): [T("side_rec") if s_ > 0 else T("side_pay") for s_, _, _ in legs],
                            T("notional"): [n_ for _, n_, _ in legs], "PV01 $": [s_ * n_ * curve.annuity(t_, freq) * 1e-4 for s_, n_, t_ in legs]})
        d1, d2 = st.columns([1.3, 1], gap="large")
        d1.dataframe(ctd.style.format({T("notional"): "{:,.0f}", "PV01 $": "{:+,.0f}"}), hide_index=True, width="stretch")
        sdf = pd.DataFrame(scen_rows, columns=[T("dk_ct_move_fly") if kind == "fly" else T("dk_ct_move"), "P&L $"])
        d2.dataframe(sdf.style.format({sdf.columns[0]: "{:+.0f} bp", "P&L $": "{:+,.0f}"}), hide_index=True, width="stretch")
        net = sum(s_ * n_ * curve.annuity(t_, freq) * 1e-4 for s_, n_, t_ in legs)
        ui.note(T("dk_ct_note", net=f"{net:+,.2f}", zdv=f"{K.zero_dv01(curve, f):+,.0f}"))


# ============================================================================================ FRA / futures
@st.fragment
def _fra(T, th, curve, freq):
    c = st.columns([1, 1, 1, 1])
    t1 = c[0].number_input(T("dk_fra_start"), 0.25, float(curve.tmax - 0.25), min(2.0, float(curve.tmax - 0.25)), 0.25, key="dk_fra_t1")
    ln = c[1].select_slider(T("dk_fra_len"), [0.25, 0.5, 1.0], 0.25, key="dk_fra_len", format_func=lambda x: f"{x*12:g}M")
    t2 = t1 + ln
    if t2 > curve.tmax + 1e-9:
        ui.note(T("dk_fra_range"), "warn")
        return
    fair = K.fra_rate(curve, t1, t2) * 100
    N = c[2].number_input(T("notional"), 1e5, 1e10, 1e7, 1e6, format="%.0f", key="dk_fra_n")
    Kc = c[3].number_input(T("dk_fra_k"), -5.0, 30.0, round(fair, 4), 0.01, format="%.4f", key=f"dk_fra_k_{round(fair, 3)}")
    side = st.segmented_control(T("side"), ["pay", "rec"], default="pay", key="dk_fra_side", format_func=lambda x: T("dk_fra_" + x)) or "pay"
    pf = side == "pay"
    f = lambda cu: K.fra_value(cu, N, Kc / 100, t1, t2, pf)
    v = f(curve)
    dv = K.zero_dv01(curve, f)
    ui.kpi_strip(th, [
        {"label": T("dk_fra_fair"), "value": fair, "dec": 4, "suffix": "%", "sub": T("dk_fra_fair_s")},
        {"label": T("dk_fra_pv"), "value": v, "dec": 0, "prefix": "$", "tone": "pos" if v >= 0 else "neg", "sub": T("mtm")},
        {"label": "DV01", "value": dv, "dec": 0, "prefix": "$", "sub": T("per_bp")},
        {"label": T("dk_fra_diff"), "value": (fair - Kc) * 100, "dec": 1, "suffix": " bp", "sub": T("dk_fra_diff_s")},
    ])
    st.markdown(f"**{T('dk_cx_title')}**")
    sg = st.slider(T("dk_cx_sigma"), 10, 250, 100, 5, key="dk_cx_sig", help=T("dk_cx_help")) / 1e4
    t1s = np.array([x for x in (0.5, 1, 2, 3, 5, 8, 10) if x + 0.25 <= curve.tmax + 1e-9], float)
    fw = np.array([curve.forward(t, t + 0.25, "cc") for t in t1s])
    cx = np.array([K.ho_lee_convexity(sg, t, t + 0.25) for t in t1s])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"{t:g}Y" for t in t1s], y=cx * 1e4, marker=dict(color=th["accent"], cornerradius=4), hovertemplate="%{y:.2f} bp<extra></extra>"))
    fig.update_layout(**ui.plotly_layout(th, 260, showlegend=False, hovermode="closest", yaxis_title="bp", title=dict(text=T("dk_cx_chart"), font=dict(size=14))))
    g1, g2 = st.columns([1, 1.2], gap="large")
    g1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    tb = pd.DataFrame({T("dk_cx_exp"): [f"{t:g}Y" for t in t1s], T("dk_cx_fwd"): fw * 100, T("dk_cx_adj"): cx * 1e4, T("dk_cx_fut"): (fw + cx) * 100})
    g2.dataframe(tb.style.format({T("dk_cx_fwd"): "{:.4f}%", T("dk_cx_adj"): "{:.2f} bp", T("dk_cx_fut"): "{:.4f}%"}), hide_index=True, width="stretch")
    ui.note(T("dk_cx_note"))
