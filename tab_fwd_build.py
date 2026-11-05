"""Tab 2 - 'Build your own forward' (custom): asset class presets, discrete income / costs, term-structure discounting,
frictions band, risk (greeks, VaR, scenario grid), replication and implied-parameter analytics."""
from __future__ import annotations
from dataclasses import replace
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import norm

import qd_fwd as F
import qd_ui as ui

# S, days, q%, u%, y%, b%, income(n, amt, first_day, every_day), cost(n, amt, first_day, every_day), unit label
PRESETS = {
    "equity": dict(S=50.0, days=304, q=0.0, u=0.0, y=0.0, b=0.0, inc=(3, 0.75, 91, 91), cost=(0, 0.0, 91, 91), unit="$ / share", qty=1000.0),
    "index": dict(S=5500.0, days=182, q=1.4, u=0.0, y=0.0, b=0.0, inc=(0, 0.0, 91, 91), cost=(0, 0.0, 91, 91), unit="index pts", qty=50.0),
    "fx": dict(S=1.08, days=365, q=3.0, u=0.0, y=0.0, b=0.0, inc=(0, 0.0, 91, 91), cost=(0, 0.0, 91, 91), unit="USD per EUR", qty=1_000_000.0),
    "commodity": dict(S=80.0, days=270, q=0.0, u=2.0, y=3.0, b=0.0, inc=(0, 0.0, 91, 91), cost=(0, 0.0, 91, 91), unit="$ / unit", qty=1000.0),
    "bond": dict(S=100.0, days=365, q=0.0, u=0.0, y=0.0, b=0.0, inc=(2, 2.0, 182, 182), cost=(0, 0.0, 91, 91), unit="price", qty=10_000.0),
}


def _gen(n, amt, first, every):
    return pd.DataFrame({"day": [int(first + k * every) for k in range(int(n))], "amount": [float(amt)] * int(n)})


def _flow_editor(T, key, title_key, preset_vals, asset):
    """Generator (count, amount, first day, spacing) + editable table. Returns tuple of (t_years, amount)."""
    dfk, vk = f"fb_{key}_{asset}_df", f"fb_{key}_{asset}_ver"
    if dfk not in st.session_state:
        st.session_state[dfk] = _gen(*preset_vals)
        st.session_state[vk] = 0
    st.markdown(f"**{T(title_key)}**")
    g = st.columns(4)
    n = g[0].number_input(T("fb_n"), 0, 60, int(preset_vals[0]), 1, key=f"fb_{key}_{asset}_n")
    a = g[1].number_input(T("fb_amt"), 0.0, 1e9, float(preset_vals[1]), 0.05, format="%.4f", key=f"fb_{key}_{asset}_a")
    f0 = g[2].number_input(T("fb_first"), 1, 3650, int(preset_vals[2]), 1, key=f"fb_{key}_{asset}_f")
    ev = g[3].number_input(T("fb_every"), 1, 3650, int(preset_vals[3]), 1, key=f"fb_{key}_{asset}_e")
    if st.button(T("fb_gen"), key=f"fb_{key}_{asset}_gen", width="stretch"):
        st.session_state[dfk] = _gen(n, a, f0, ev)
        st.session_state[vk] += 1
        st.rerun()
    df = st.data_editor(st.session_state[dfk], hide_index=True, width="stretch", num_rows="dynamic", key=f"fb_{key}_{asset}_ed{st.session_state[vk]}",
                        height=min(36 * (len(st.session_state[dfk]) + 2), 220),
                        column_config={"day": st.column_config.NumberColumn(T("fb_day"), min_value=1, max_value=3650, format="%d"),
                                       "amount": st.column_config.NumberColumn(T("fb_amount"), format="%.4f")})
    df = df.dropna()
    return tuple((float(r.day) / 365.0, float(r.amount)) for r in df.itertuples() if r.amount != 0)


def render(T, th, curve):
    st.caption(T("fb_sub"))
    # -------------------------------------------------------------------- 1. what is being priced
    with st.container(border=True):
        asset = st.segmented_control(T("fb_asset"), list(PRESETS), default="equity", key="fb_asset", format_func=lambda x: T("fb_a_" + x)) or "equity"
        P0 = PRESETS[asset]
        h = st.columns(4)
        pos = h[0].segmented_control(T("position"), [1, -1], default=1, key="fb_pos", format_func=lambda x: T("long") if x == 1 else T("short")) or 1
        qty = h[1].number_input(T("fb_qty"), 1.0, 1e12, float(P0["qty"]), format="%.0f", key=f"fb_qty_{asset}", help=T("fb_qty_help"))
        S = h[2].number_input(T("spot_px"), 1e-6, 1e9, float(P0["S"]), format="%.4f", key=f"fb_S_{asset}")
        days = h[3].number_input(T("fb_days"), 1, 3650, int(P0["days"]), 1, key=f"fb_days_{asset}", help=T("fb_days_help"))
        Tm = days / 365.0
        m = st.columns(4)
        q = m[0].number_input(T("fb_q_" + asset), -20.0, 60.0, float(P0["q"]), 0.05, format="%.3f", key=f"fb_q_{asset}", help=T("fb_q_help")) / 100
        u = m[1].number_input(T("storage"), -20.0, 60.0, float(P0["u"]), 0.05, format="%.3f", key=f"fb_u_{asset}", help=T("storage_help")) / 100
        y = m[2].number_input(T("cy"), -30.0, 60.0, float(P0["y"]), 0.05, format="%.3f", key=f"fb_y_{asset}", help=T("cy_help")) / 100
        b = m[3].number_input(T("fb_b"), -20.0, 60.0, float(P0["b"]), 0.05, format="%.3f", key=f"fb_b_{asset}", help=T("fb_b_help")) / 100
        m2 = st.columns(4)
        rmode = m2[0].segmented_control(T("fb_disc"), ["curve", "flat"], default="curve", key="fb_rmode", format_func=lambda x: T("fb_d_" + x)) or "curve"
        z_def = float(curve.zero(max(Tm, 0.02), "cc")) * 100 if curve is not None else 4.0
        r_flat = m2[1].number_input(T("fb_rflat"), -5.0, 40.0, round(z_def, 3), 0.05, format="%.3f", disabled=rmode != "flat", key=f"fb_rflat_{asset}_{round(z_def, 2)}") / 100
        sprd = m2[2].number_input(T("fb_spread"), -500.0, 1000.0, 0.0, 1.0, format="%.1f", key="fb_spread", help=T("fb_spread_help")) / 1e4
        sig = m2[3].number_input(T("fb_vol"), 0.5, 300.0, 25.0 if asset in ("equity", "commodity") else 15.0 if asset == "index" else 8.0 if asset == "fx" else 6.0, 0.5,
                                 format="%.1f", key=f"fb_vol_{asset}", help=T("fb_vol_help")) / 100
    base_P = (lambda t: float(curve.df_at(max(t, 0.0)))) if (rmode == "curve" and curve is not None) else (lambda t, r0=(r_flat if rmode == "flat" else 0.04): float(np.exp(-r0 * t)))
    P = lambda t, bp=base_P, s=sprd: bp(t) * float(np.exp(-s * t))

    ex = st.columns(2, gap="large")
    with ex[0]:
        with st.expander(T("fb_inc_title"), expanded=asset in ("equity", "bond")):
            income = _flow_editor(T, "inc", "fb_inc_hdr", P0["inc"], asset)
            st.caption(T("fb_inc_help"))
    with ex[1]:
        with st.expander(T("fb_cost_title"), expanded=False):
            costs = _flow_editor(T, "cost", "fb_cost_hdr", P0["cost"], asset)
            st.caption(T("fb_cost_help"))
    late = sum(1 for t_, _ in income + costs if t_ > Tm + 1e-12)
    if late:
        ui.note(T("fb_late", n=late), "warn")

    spec = F.FwdSpec(S, Tm, q, u, y, b, income, costs)
    Ffair = F.fwd_price(spec, P)
    dec = F.fwd_decomposition(spec, P)
    if dec["S_adj"] <= 0:
        ui.note(T("fb_neg_adj"), "neg")
        return

    # -------------------------------------------------------------------- 2. market quote, strike
    k1 = st.columns([1, 1, 1, 1])
    use_mkt = k1[0].toggle(T("fb_have_mkt"), False, key="fb_have_mkt", help=T("fb_have_mkt_help"))
    Fmk = k1[1].number_input(T("mkt_f"), 1e-6, 1e12, float(round(Ffair, 4)), format="%.4f", disabled=not use_mkt, key=f"fb_Fm_{asset}_{round(Ffair, 3)}") if use_mkt else Ffair
    ks = k1[2].segmented_control(T("strike_mode"), ["mkt", "fair", "custom"], default="mkt", key="fb_kmode", format_func=lambda x: T("km_" + x)) or "mkt"
    K = Fmk if ks == "mkt" else Ffair if ks == "fair" else k1[3].number_input(T("strike"), 1e-6, 1e12, float(round(Ffair, 4)), format="%.4f", key=f"fb_K_{asset}")
    V = F.fwd_value_general(spec, K, P, pos, qty)
    st_ = F.fwd_basis_stats(spec, Ffair, P)
    gr = F.fwd_greeks(spec, K, P, pos, qty)

    ui.kpi_strip(th, [
        {"label": T("fair_f"), "value": Ffair, "dec": 4 if Ffair < 100 else 2, "sub": f"T={Tm:.3f}y · P(T)={P(Tm):.5f}"},
        {"label": T("mtm"), "value": V, "dec": 0, "prefix": "$", "tone": "pos" if V >= 0 else "neg", "sub": f"K={K:,.4f}"},
        {"label": T("fb_points"), "value": st_["points"], "dec": 4 if abs(st_["points"]) < 100 else 2, "sub": f"{st_['basis_pct']:+.3f}% " + T("fb_vs_spot")},
        {"label": T("fb_basis_ann"), "value": st_["basis_ann_cc"] * 100, "dec": 3, "suffix": "%", "sub": T("cc")},
        {"label": T("fb_netcarry"), "value": st_["net_carry_cc"] * 100, "dec": 3, "suffix": "%", "sub": T("fb_vs_zero", z=f"{st_['zero_cc']*100:.2f}")},
        {"label": T("fb_pv_inc"), "value": dec["PV_income"] - dec["PV_costs"], "dec": 4, "sub": T("fb_pv_inc_sub")},
    ])

    tabs = st.tabs([T("fb_t_price"), T("fb_t_risk"), T("fb_t_term"), T("fb_t_repl"), T("fb_t_arb")])
    # ================================================================ pricing
    with tabs[0]:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            names = [T("fb_w_spot"), T("fb_w_inc"), T("fb_w_cost"), T("fb_w_carry"), T("fb_w_fin"), T("fb_w_F")]
            vals = [S, -dec["PV_income"], dec["PV_costs"], dec["d_carry"], dec["d_fin"], None]
            fig = go.Figure(go.Waterfall(x=names, measure=["absolute", "relative", "relative", "relative", "relative", "total"], y=vals,
                                         increasing=dict(marker=dict(color=th["pos"])), decreasing=dict(marker=dict(color=th["neg"])),
                                         totals=dict(marker=dict(color=th["accent"])), connector=dict(line=dict(color=th["grid"])),
                                         hovertemplate="%{x}: %{y:,.4f}<extra></extra>"))
            lo_ = min(S, Ffair, dec["S_adj"])
            fig.update_layout(**ui.plotly_layout(th, 340, title=dict(text=T("fb_build_title"), font=dict(size=14)), showlegend=False, hovermode="closest"))
            fig.update_yaxes(range=[lo_ - max(abs(Ffair - S) * 3, S * 0.02), max(S, Ffair) + max(abs(Ffair - S) * 1.5, S * 0.02)])
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with c2:
            Sg = np.linspace(S * 0.7, S * 1.3, 121)
            mtm = [F.fwd_value_general(replace(spec, S=s_), K, P, pos, qty) for s_ in Sg]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=Sg, y=F.payoff_curve(Sg, K, pos, qty), name=T("payoff_T"), line=dict(color=th["c"][2], width=2, dash="dash"), hovertemplate="$%{y:,.0f}"))
            fig.add_trace(go.Scatter(x=Sg, y=mtm, name=T("mtm_now"), line=dict(color=th["accent"], width=3), hovertemplate="$%{y:,.0f}"))
            fig.add_vline(x=S, line=dict(color=th["mute"], width=1, dash="dot"), annotation_text=T("spot"), annotation_font_color=th["mute"])
            fig.add_hline(y=0, line=dict(color=th["grid"], width=1))
            fig.update_layout(**ui.plotly_layout(th, 340, title=dict(text=T("fb_pay_title"), font=dict(size=14)), xaxis_title=T("spot_at"), yaxis_title="P&L $"))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        im = F.fwd_implied(spec, Fmk, P)
        rows = [(T("fb_i_carry"), im["carry"] * 100), (T("fb_i_y"), im["y"] * 100), (T("fb_i_q"), im["q"] * 100), (T("fb_i_u"), im["u"] * 100),
                (T("fb_i_b"), im["b"] * 100), (T("fb_i_repo"), im["implied_repo"] * 100), (T("fb_i_spread"), im["fin_spread"] * 1e4),
                (T("fb_i_pvinc"), im["pv_income_implied"])]
        units = ["%", "%", "%", "%", "%", "%", "bp", ""]
        tb = pd.DataFrame({T("fb_param"): [r_[0] for r_ in rows], T("fb_implied"): [r_[1] for r_ in rows], T("fb_unit"): units,
                           T("fb_input"): [spec.carry * 100, y * 100, q * 100, u * 100, b * 100, -np.log(P(Tm)) / Tm * 100, sprd * 1e4, dec["PV_income"] - dec["PV_costs"]]})
        st.markdown(f"**{T('fb_impl_title')}**")
        st.dataframe(tb.style.format({T("fb_implied"): "{:,.4f}", T("fb_input"): "{:,.4f}"}), hide_index=True, width="stretch")
        ui.note(T("fb_impl_note"))

    # ================================================================ risk
    with tabs[1]:
        lab_q = T("fb_q_" + asset)
        ui.kpi_strip(th, [
            {"label": "Δ", "value": gr["delta"], "dec": 2, "sub": T("units_per_usd")},
            {"label": "Rho 1bp", "value": gr["rho_1bp"], "dec": 0, "prefix": "$", "sub": T("fb_parallel")},
            {"label": T("fb_q01_" + asset), "value": gr["q01"], "dec": 0, "prefix": "$", "sub": T("per_bp")},
            {"label": T("yield01"), "value": gr["y01"], "dec": 0, "prefix": "$", "sub": T("per_bp")},
            {"label": T("fb_stor01"), "value": gr["u01"], "dec": 0, "prefix": "$", "sub": T("per_bp")},
            {"label": T("fb_b01"), "value": gr["b01"], "dec": 0, "prefix": "$", "sub": T("per_bp")},
            {"label": "Θ/" + T("day"), "value": gr["theta_day"], "dec": 0, "prefix": "$", "sub": T("carry_decay")},
        ])
        a, b_ = st.columns(2, gap="large")
        with a:
            st.markdown(f"**{T('fb_grid_title')}**")
            mv = np.array([-0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2])
            rs = np.array([-200, -100, -50, 0, 50, 100, 200.0])
            shift = lambda P_, dr: (lambda t: P_(t) * np.exp(-dr * t))
            Z = np.array([[F.fwd_value_general(replace(spec, S=S * (1 + m_)), K, shift(P, r_ / 1e4), pos, qty) - V for m_ in mv] for r_ in rs])
            fig = go.Figure(go.Heatmap(z=Z, x=mv * 100, y=rs, zmid=0, xgap=1, ygap=1, colorscale=[[0, th["neg"]], [0.5, th["panel2"]], [1, th["pos"]]],
                                       hovertemplate=T("fb_grid_hover") + "<extra></extra>", colorbar=dict(thickness=8, len=0.8, tickformat="$,.0f")))
            fig.update_layout(**ui.plotly_layout(th, 340, hovermode="closest", xaxis_title=T("spot_move"), yaxis_title=T("fb_rate_shift"), xaxis=dict(ticksuffix="%")))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with b_:
            c = st.columns(2)
            conf = c[0].selectbox(T("fb_conf"), [90.0, 95.0, 97.5, 99.0], index=3, format_func=lambda x: f"{x:g}%", key="fb_conf")
            hd = c[1].number_input(T("fb_hz"), 1, 365, 10, 1, key="fb_hz")
            lam = st.slider(T("fb_lambda"), -10.0, 10.0, 0.0, 0.5, key="fb_lam", help=T("fb_lambda_help")) / 100
            # distribution of P&L at maturity: S_T lognormal with E[S_T] = F e^{lambda T}
            mu_ln = np.log(Ffair) + lam * Tm - 0.5 * sig ** 2 * Tm
            sd = sig * np.sqrt(Tm)
            zq = norm.ppf(np.linspace(0.001, 0.999, 400))
            ST = np.exp(mu_ln + sd * zq)
            dens = norm.pdf(zq) / (sd * ST)
            pl = pos * qty * (ST - K)
            order = np.argsort(pl)
            jac = dens / (qty)
            p_win = float(norm.cdf((mu_ln - np.log(K)) / sd)) if pos == 1 else float(norm.cdf((np.log(K) - mu_ln) / sd))
            E_pl = pos * qty * (Ffair * np.exp(lam * Tm) - K)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=pl[order], y=jac[order], fill="tozeroy", fillcolor=th["accent_a"], line=dict(color=th["accent"], width=2.4), name=T("fb_dist"), hovertemplate="$%{x:,.0f}<extra></extra>"))
            fig.add_vline(x=0, line=dict(color=th["grid"], width=1))
            fig.add_vline(x=E_pl, line=dict(color=th["warn"], width=1.4, dash="dash"), annotation_text=T("fb_exp"), annotation_font_color=th["warn"])
            fig.update_layout(**ui.plotly_layout(th, 270, title=dict(text=T("fb_dist_title"), font=dict(size=14)), showlegend=False, hovermode="closest", xaxis_title=T("fb_pl_T")))
            fig.update_yaxes(showticklabels=False)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        # VaR over horizon: exact revaluation at the lognormal quantile of the spot (zero drift over the horizon)
        hy = hd / 365.0
        zc = norm.ppf(conf / 100.0)
        s_lo, s_hi = S * np.exp(-0.5 * sig ** 2 * hy - zc * sig * np.sqrt(hy)), S * np.exp(-0.5 * sig ** 2 * hy + zc * sig * np.sqrt(hy))
        v_lo, v_hi = (F.fwd_value_general(replace(spec, S=s_), K, P, pos, qty) for s_ in (s_lo, s_hi))
        var_ = max(V - min(v_lo, v_hi), 0.0)
        ui.kpi_strip(th, [
            {"label": T("fb_var", c=f"{conf:g}", d=hd), "value": var_, "dec": 0, "prefix": "$", "tone": "neg", "sub": T("fb_var_sub")},
            {"label": T("fb_ev"), "value": E_pl, "dec": 0, "prefix": "$", "tone": "pos" if E_pl >= 0 else "neg", "sub": T("fb_ev_sub")},
            {"label": T("fb_pwin"), "value": p_win * 100, "dec": 1, "suffix": "%", "sub": T("fb_pwin_sub")},
            {"label": T("fb_sd_T"), "value": qty * Ffair * np.exp(lam * Tm) * float(np.sqrt(np.expm1(sig ** 2 * Tm))), "dec": 0, "prefix": "$", "sub": T("fb_sd_sub")},
        ])
        ui.note(T("fb_risk_note", rho=f"{gr['rho_1bp']:,.0f}", q=f"{gr['q01']:,.0f}"))

    # ================================================================ term structure
    with tabs[2]:
        tmax = float(max(Tm * 2.0, 1.0)) if curve is None else float(min(max(Tm * 2.0, 1.0), curve.tmax))
        tg = np.unique(np.r_[np.linspace(max(tmax / 60, 1 / 365), tmax, 60), Tm])
        Fs = F.fwd_curve(spec, P, tg)
        zs = np.array([-np.log(P(t)) / t for t in tg])
        basis = np.log(Fs / S) / tg
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tg, y=Fs, name=T("theo"), line=dict(color=th["accent"], width=3), hovertemplate="%{y:,.4f}"))
        fig.add_trace(go.Scatter(x=[0, tg[-1]], y=[S, S], name=T("spot"), line=dict(color=th["mute"], width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=[Tm], y=[Fmk], mode="markers", name=T("fb_this"), marker=dict(size=12, color=th["warn"], line=dict(color=th["bg"], width=2))))
        for t_, a_ in income:
            if t_ <= tg[-1]:
                fig.add_vline(x=t_, line=dict(color=th["c"][3], width=1, dash="dot"))
        fig.update_layout(**ui.plotly_layout(th, 340, xaxis_title=T("maturity"), yaxis_title=T("fb_price_axis")))
        c1, c2 = st.columns([1.5, 1], gap="large")
        c1.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        fb = go.Figure()
        fb.add_trace(go.Scatter(x=tg, y=zs * 100, name=T("fb_zero"), line=dict(color=th["c"][1], width=2.2), hovertemplate="%{y:.3f}%"))
        fb.add_trace(go.Scatter(x=tg, y=basis * 100, name=T("fb_basis_ann"), line=dict(color=th["accent"], width=2.8), hovertemplate="%{y:.3f}%"))
        fb.add_trace(go.Scatter(x=tg, y=np.full_like(tg, spec.carry * 100), name=T("fb_carry_cc"), line=dict(color=th["c"][2], width=1.6, dash="dash"), hovertemplate="%{y:.3f}%"))
        fb.update_layout(**ui.plotly_layout(th, 340, xaxis_title=T("maturity"), yaxis_title="%", title=dict(text=T("fb_basis_title"), font=dict(size=14))))
        c2.plotly_chart(fb, width="stretch", config={"displayModeBar": False})
        std_t = [t_ for t_ in (1 / 12, 0.25, 0.5, 1, 2, 3, 5) if t_ <= tmax + 1e-9]
        ts = pd.DataFrame({"T": std_t, "P(0,T)": [P(t) for t in std_t], "F": F.fwd_curve(spec, P, std_t)})
        ts["pts"] = ts["F"] - S
        ts["basis_ann_%"] = np.log(ts["F"] / S) / ts["T"] * 100
        st.dataframe(ts.style.format({"T": "{:.3f}", "P(0,T)": "{:.6f}", "F": "{:,.4f}", "pts": "{:+,.4f}", "basis_ann_%": "{:+.3f}"}), hide_index=True, width="stretch")
        st.download_button(T("fb_csv"), pd.DataFrame({"T": tg, "P": [P(t) for t in tg], "F": Fs, "basis_ann": basis}).to_csv(index=False).encode(), "forward_term_structure.csv", "text/csv")

    # ================================================================ replication
    with tabs[3]:
        r1, r2 = st.columns([1, 3])
        with r1:
            steps = st.slider(T("periods"), 2, 12, 4, key="fb_steps")
            pmode = st.selectbox(T("path"), ["carry", "up", "down", "wave"], format_func=lambda x: T("p_" + x), key="fb_path")
        ts_ = np.linspace(0, Tm, steps + 1)
        carry_path = S * np.exp(np.log(Ffair / S) * ts_ / Tm)
        path = {"carry": carry_path, "up": S * (1 + 0.25 * ts_ / Tm), "down": S * (1 - 0.25 * ts_ / Tm), "wave": S * (1 + 0.12 * np.sin(2 * np.pi * ts_ / Tm))}[pmode]
        path[0] = S
        tab, chk = F.replication_general(spec, K, P, steps, path, pos)
        lab = {"S": "fb_r_S", "n": "fb_r_n", "asset": "fb_r_asset", "inc": "fb_r_inc", "cost": "fb_r_cost", "loan": "fb_r_loan", "port": "fb_r_port", "fwd": "fb_r_fwd"}
        tab.index = [T(lab[i]) for i in tab.index]
        hi_ = {T("fb_r_port"), T("fb_r_fwd")}
        with r2:
            st.dataframe(tab.style.format("{:,.4f}").apply(lambda s_: ["font-weight:700" if s_.name in hi_ else "" for _ in s_], axis=1), width="stretch", height=min(35 * (len(tab) + 1) + 3, 360))
            ui.note(T("repl_note", err=f"{chk['max_abs_err']:.1e}"), "pos" if chk["max_abs_err"] < 1e-8 else "neg")
        ui.note(T("fb_repl_help"))

    # ================================================================ arbitrage band
    with tabs[4]:
        f1 = st.columns(4)
        hs = f1[0].number_input(T("fb_fr_hs"), 0.0, 1000.0, 5.0, 0.5, format="%.1f", key="fb_hs", help=T("fb_fr_hs_help")) / 1e4
        sb = f1[1].number_input(T("fb_fr_sb"), 0.0, 1000.0, 25.0, 1.0, format="%.1f", key="fb_sb", help=T("fb_fr_sb_help")) / 1e4
        sl = f1[2].number_input(T("fb_fr_sl"), 0.0, 1000.0, 25.0, 1.0, format="%.1f", key="fb_sl", help=T("fb_fr_sl_help")) / 1e4
        fee = f1[3].number_input(T("fb_fr_fee"), 0.0, 1e6, 0.0, 0.01, format="%.4f", key="fb_fee", help=T("fb_fr_fee_help"))
        lo, up = F.fwd_band(spec, P, hs, sb, sl, fee)
        fig = go.Figure()
        fig.add_shape(type="rect", x0=lo, x1=up, y0=0, y1=1, fillcolor=th["accent_a"], line=dict(width=0))
        same = abs(Fmk - Ffair) < 1e-3 * max(up - lo, 1e-9)
        for x_, nm, col, dsh, pos_ in ((lo, T("fb_f_dn"), th["c"][1], "dash", "top"), (Ffair, T("fair_f") + (" = " + T("mkt_f") if same else ""), th["accent"], "solid", "top"),
                                       (up, T("fb_f_up"), th["c"][2], "dash", "top"), (Fmk, T("mkt_f"), th["warn"], "solid", "bottom")):
            if same and nm == T("mkt_f"):
                continue
            fig.add_vline(x=x_, line=dict(color=col, width=2.4 if dsh == "solid" else 1.6, dash=dsh), annotation_text=f"{nm}<br>{x_:,.4f}", annotation_font_color=col, annotation_position=pos_)
        pad = max(up - lo, abs(Fmk - Ffair)) * 0.6 + 1e-9
        fig.update_xaxes(range=[min(lo, Fmk) - pad, max(up, Fmk) + pad], gridcolor=th["grid"])
        fig.update_yaxes(visible=False, range=[0, 1])
        fig.update_layout(**ui.plotly_layout(th, 190, showlegend=False, hovermode=False, margin=dict(l=8, r=8, t=60, b=8)))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        if Fmk > up + 1e-12:
            sig_, prof = "cash_and_carry", (Fmk - up)
        elif Fmk < lo - 1e-12:
            sig_, prof = "reverse_cash_and_carry", (lo - Fmk)
        else:
            sig_, prof = "none", 0.0
        gap = Fmk - Ffair
        ui.kpi_strip(th, [
            {"label": T("signal"), "value": None, "sub": T("sig_" + sig_) if sig_ != "none" else T("fb_inside")},
            {"label": T("fb_gap_fair"), "value": gap, "dec": 4, "sub": f"{gap / S * 1e4:+.1f} bp " + T("fb_vs_spot")},
            {"label": T("fb_net_profit"), "value": prof * qty, "dec": 0, "prefix": "$", "tone": "pos" if prof > 0 else "", "sub": T("at_T")},
            {"label": T("locked_pv"), "value": prof * qty * P(Tm), "dec": 0, "prefix": "$", "tone": "pos" if prof > 0 else "", "sub": T("today")},
            {"label": T("fb_band_w"), "value": (up - lo) / S * 1e4, "dec": 1, "suffix": " bp", "sub": T("fb_band_sub")},
        ])
        ui.note(T("fb_arb_note"), "warn" if sig_ != "none" else "")
    with st.expander(T("fb_refs")):
        st.markdown(T("fb_refs_body").replace("$", "\\$"))
