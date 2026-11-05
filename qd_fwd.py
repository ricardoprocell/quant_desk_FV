"""Quant Desk - forwards / futures on storable commodities (cost of carry, replication, arbitrage)."""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
import pandas as pd


def fair_forward(S, r, T, u=0.0, y=0.0):
    """F = S e^{(r+u-y)T}; r cc risk-free, u storage cost, y convenience yield (cc, annual)."""
    return S * np.exp((r + u - y) * T)


def implied_yield(S, F, r, T, u=0.0):
    """Net convenience yield y that makes F fair (cc): y = r + u - ln(F/S)/T."""
    return r + u - np.log(F / S) / T


def implied_repo(S, F, T, u=0.0, y=0.0):
    """Financing rate implied by market F: r = ln(F/S)/T - u + y."""
    return np.log(F / S) / T - u + y


def forward_value(S, K, r, T, u=0.0, y=0.0, pos=1, qty=1.0):
    """MTM of a forward struck at K, maturity T remaining: pos*(F-K)e^{-rT}*qty. Greeks per unit."""
    F = fair_forward(S, r, T, u, y)
    pv = np.exp(-r * T)
    v = pos * qty * (F - K) * pv
    delta = pos * qty * np.exp((u - y) * T)                 # dV/dS
    # rho: d/dr[(S e^{(r+u-y)T} - K) e^{-rT}] = d/dr[S e^{(u-y)T} - K e^{-rT}] = K T e^{-rT}
    rho = pos * qty * K * T * pv
    theta = pos * qty * (-(u - y) * S * np.exp((u - y) * T) - K * r * pv)  # dV/dt (calendar), per year
    # carry sensitivities (per 1bp): V = n(S e^{(u-y)T}) - K e^{-rT}
    yield01 = -pos * qty * T * S * np.exp((u - y) * T) * 1e-4
    storage01 = pos * qty * T * S * np.exp((u - y) * T) * 1e-4
    return {"F": F, "value": v, "delta": delta, "rho_1bp": rho * 1e-4, "theta_day": theta / 365.0,
            "yield_1bp": yield01, "storage_1bp": storage01}


def payoff_curve(Sgrid, K, pos=1, qty=1.0):
    return pos * qty * (np.asarray(Sgrid) - K)


def term_structure(S, r_fn, tenors, u=0.0, y=0.0):
    """Theoretical forward curve; r_fn(T) returns cc zero rate."""
    return pd.DataFrame({"T": tenors, "r": [r_fn(t) for t in tenors],
                         "F": [fair_forward(S, r_fn(t), t, u, y) for t in tenors]})


def arbitrage(S, F_mkt, r, T, u=0.0, y=0.0, qty=1.0, tol_bp=0.0):
    """No-fee cash-and-carry test. Returns dict with signal and locked-in profit at T (and PV).
    F_mkt > F_fair -> cash & carry: borrow S, buy spot, short forward. F_mkt < F_fair -> reverse."""
    F = fair_forward(S, r, T, u, y)
    gap = F_mkt - F
    pv = gap * np.exp(-r * T) * qty
    sig = "none"
    if abs(gap) / S * 1e4 > tol_bp:
        sig = "cash_and_carry" if gap > 0 else "reverse_cash_and_carry"
    return {"F_fair": F, "F_mkt": F_mkt, "gap": gap, "gap_pct": gap / F, "profit_T": gap * qty, "profit_pv": pv, "signal": sig}


def replication_table(S0, K, r, T, u=0.0, y=0.0, steps=4, pos=1, path=None):
    """Replicating portfolio of a LONG forward (struck K, delivery T): hold n_t=e^{-(y-u)(T-t)} units, borrow K e^{-r(T-t)}.
    Rows = movements, columns = t. `path` = spot at each t (default: grows at r+u-y, i.e. spot follows carry).
    Value of replicating portfolio equals the forward value at every date. Returns (DataFrame, check_dict)."""
    ts = np.linspace(0, T, steps + 1)
    if path is None:
        path = S0 * np.exp((r + u - y) * ts)
    path = np.asarray(path, float)
    rem = T - ts
    n = np.exp((u - y) * rem)              # units of commodity held (storage cost u shrinks cash/units, yield y adds)
    loan = K * np.exp(-r * rem)            # PV of strike owed
    stock = n * path
    val = stock - loan
    F_t = path * np.exp((r + u - y) * rem)
    fwd = (F_t - K) * np.exp(-r * rem)
    rows = {
        "Spot S_t": path,
        "Units held n_t": n,
        "Commodity position  n_t·S_t": stock,
        "Loan  −K e^{−r(T−t)}": -loan,
        "Portfolio value": val,
        "Forward value (F_t−K)e^{−r(T−t)}": fwd,
    }
    # rebalancing flows between dates: buy/sell units, financed by loan change (self-financing at fixed path)
    dn = np.r_[n[0], np.diff(n)]
    rows["Δ units (trade)"] = dn
    rows["Trade cash  −Δn·S_t"] = -dn * path
    dl = np.r_[-loan[0], -np.diff(loan)]
    rows["Loan accrual/Δ"] = dl
    df = pd.DataFrame(rows, index=None).T
    df.columns = [f"t={t:.2f}" for t in ts]
    df = df * 1.0
    if pos == -1:
        df.loc[["Commodity position  n_t·S_t", "Loan  −K e^{−r(T−t)}", "Portfolio value", "Forward value (F_t−K)e^{−r(T−t)}"]] *= -1
    return df, {"max_abs_err": float(np.max(np.abs(val - fwd))), "ts": ts}


def futures_vs_forward_note():
    return "With deterministic rates futures price = forward price; daily margining only shifts cash timing."


# =====================================================================================================
# General forward builder
# =====================================================================================================
# Reference: Hull, Options, Futures and Other Derivatives, ch. 5 (forward prices, known income, known yield,
# storage costs, convenience yield, FX / covered interest parity).  With a discount function P(0,t):
#
#       F0 = ( S0 - PV(income) + PV(storage) ) * exp( c T ) / P(0,T) ,     c = u - y - q - b
#
#   S0 spot | PV(income)=sum D_i P(0,t_i) known cash income (dividends, coupons) paid at t_i <= T
#   PV(storage)=sum U_i P(0,t_i) known storage / insurance costs | u proportional storage cost (cc)
#   y convenience yield (cc) | q continuous yield (dividend yield on an index, foreign rate for FX) | b stock-borrow fee
#   With flat cc rate r:  P(0,t)=e^{-rt}  =>  F = S e^{(r-q)T}, S e^{(r+u-y)T}, (S-I)e^{rT}, (S+U)e^{rT}, S e^{(r-r_f)T}.
@dataclass
class FwdSpec:
    S: float
    T: float
    q: float = 0.0                       # continuous yield (dividend yield / foreign rate)  [cc, annual]
    u: float = 0.0                       # proportional storage cost                         [cc, annual]
    y: float = 0.0                       # convenience yield                                 [cc, annual]
    b: float = 0.0                       # borrow / lending fee on the asset                 [cc, annual]
    income: tuple = ()                   # ((t_i, D_i), ...) cash received by the holder (dividends, coupons)
    costs: tuple = ()                    # ((t_i, U_i), ...) cash paid by the holder (storage, insurance)

    @property
    def carry(self):
        return self.u - self.y - self.q - self.b


def _flows(fl, T, t0=0.0):
    return [(float(t) - t0, float(a)) for t, a in fl if t0 < float(t) <= T + 1e-12 and float(a) != 0.0]


def pv_flows(fl, T, P, t0=0.0):
    """PV at time t0 of dated cash flows (t_i, a_i) with t0 < t_i <= T. P(t0, t) is the discount function from t0."""
    return float(sum(a * P(t) for t, a in _flows(fl, T, t0)))


def fwd_price(spec: FwdSpec, P):
    """Fair forward price. P: discount function t -> P(0,t)."""
    I = pv_flows(spec.income, spec.T, P)
    U = pv_flows(spec.costs, spec.T, P)
    return float((spec.S - I + U) * np.exp(spec.carry * spec.T) / P(spec.T))


def fwd_decomposition(spec: FwdSpec, P):
    """Step-by-step build of F: S -> -PV(inc) +PV(cost) -> carry factor -> financing factor."""
    I = pv_flows(spec.income, spec.T, P)
    U = pv_flows(spec.costs, spec.T, P)
    S_adj = spec.S - I + U
    cf = np.exp(spec.carry * spec.T)
    fin = 1.0 / P(spec.T)
    F = S_adj * cf * fin
    # additive attribution (sequential): spot -> income -> costs -> continuous carry -> financing
    steps = [("S", spec.S), ("−PV(income)", -I), ("+PV(costs)", U)]
    base = S_adj
    d_carry = base * (cf - 1.0)
    d_fin = base * cf * (fin - 1.0)
    return {"S_adj": S_adj, "PV_income": I, "PV_costs": U, "carry_factor": cf, "fin_factor": fin, "F": F,
            "d_carry": d_carry, "d_fin": d_fin, "steps": steps}


def fwd_value_general(spec: FwdSpec, K, P, pos=1, qty=1.0):
    """MTM of a forward struck at K delivering at spec.T:  pos*qty*(F-K)*P(0,T)."""
    return float(pos * qty * (fwd_price(spec, P) - K) * P(spec.T))


def fwd_greeks(spec: FwdSpec, K, P, pos=1, qty=1.0, shift=None):
    """Finite-difference sensitivities of V = pos*qty*(F-K)P(T) (central differences, tiny steps).
    shift(P, dr) -> discount function after a parallel cc zero shift dr.  Default: P'(t)=P(t)e^{-dr t}.
    delta: dV/dS | rho_1bp: +1bp parallel zero | q01, u01, y01, b01: +1bp | theta_day: 1 calendar day (time passes,
    spot, forward discount curve and the remaining cash flows held fixed)."""
    sh = shift or (lambda P_, dr: (lambda t: P_(t) * np.exp(-dr * t)))
    V = lambda s=spec, P_=P: fwd_value_general(s, K, P_, pos, qty)
    h = 1e-4
    out = {}
    out["delta"] = (V(replace(spec, S=spec.S * (1 + 1e-6))) - V(replace(spec, S=spec.S * (1 - 1e-6)))) / (2e-6 * spec.S)
    out["rho_1bp"] = (V(spec, sh(P, h)) - V(spec, sh(P, -h))) / 2.0 * (1e-4 / h)
    for nm, fld in (("q01", "q"), ("u01", "u"), ("y01", "y"), ("b01", "b")):
        out[nm] = (V(replace(spec, **{fld: getattr(spec, fld) + h})) - V(replace(spec, **{fld: getattr(spec, fld) - h}))) / 2.0 * (1e-4 / h)
    # theta: roll one day forward; discount function seen from tomorrow is the forward curve P(t+d)/P(d)
    d = 1.0 / 365.0
    if spec.T > d + 1e-9:
        Pn = lambda t: P(t + d) / P(d)
        spec_n = replace(spec, T=spec.T - d, income=tuple(_flows(spec.income, spec.T, d)), costs=tuple(_flows(spec.costs, spec.T, d)))
        out["theta_day"] = fwd_value_general(spec_n, K, Pn, pos, qty) - V()
    else:
        out["theta_day"] = float("nan")
    return out


def fwd_implied(spec: FwdSpec, F_mkt, P):
    """Back out single unknowns from a market forward (others held):
    carry c* = ln(F P(T)/S_adj)/T ; convenience yield y* = u - q - b - c* ; implied financing spread (cc) over the curve;
    implied yield q* ; implied dividend PV."""
    I = pv_flows(spec.income, spec.T, P)
    U = pv_flows(spec.costs, spec.T, P)
    S_adj = spec.S - I + U
    c_star = np.log(F_mkt * P(spec.T) / S_adj) / spec.T
    # financing spread s: F = S_adj e^{cT} e^{(z+s)T} ; z = -ln P(T)/T  =>  s = ln(F/(S_adj e^{cT}))/T - z
    z = -np.log(P(spec.T)) / spec.T
    fin_spread = np.log(F_mkt / (S_adj * np.exp(spec.carry * spec.T))) / spec.T - z
    return {"carry": float(c_star), "y": float(spec.u - spec.q - spec.b - c_star), "q": float(spec.u - spec.y - spec.b - c_star),
            "u": float(c_star + spec.y + spec.q + spec.b), "b": float(spec.u - spec.y - spec.q - c_star),
            "fin_spread": float(fin_spread), "implied_repo": float(z + fin_spread),
            "pv_income_implied": float(spec.S + U - F_mkt * np.exp(-spec.carry * spec.T) * P(spec.T))}


def fwd_band(spec: FwdSpec, P, half_spread=0.0, borrow_spread=0.0, lend_spread=0.0, fee=0.0):
    """No-arbitrage band with frictions (Hull ch.5 / Kolb: cash-and-carry vs reverse cash-and-carry):
        F_up = ( S(1+h) - I + U ) e^{cT} e^{s_b T} / P(T) + fee      (buy spot, finance at curve + s_b, sell forward)
        F_dn = ( S(1-h) - I + U ) e^{cT} e^{-s_l T} / P(T) - fee     (short spot, lend at curve - s_l, buy forward)
    h = half bid/ask spread of the underlying (fraction), s_b / s_l = financing spreads (cc), fee = round-trip cost per unit.
    With every friction zero, F_up = F_dn = F."""
    I = pv_flows(spec.income, spec.T, P)
    U = pv_flows(spec.costs, spec.T, P)
    base = np.exp(spec.carry * spec.T) / P(spec.T)
    up = (spec.S * (1 + half_spread) - I + U) * base * np.exp(borrow_spread * spec.T) + fee
    dn = (spec.S * (1 - half_spread) - I + U) * base * np.exp(-lend_spread * spec.T) - fee
    return float(dn), float(up)


def fwd_curve(spec: FwdSpec, P, tenors):
    """Forward price for a strip of maturities, keeping the cash-flow schedule (flows after T are dropped)."""
    out = []
    for t in tenors:
        sp = replace(spec, T=float(t))
        out.append(fwd_price(sp, P))
    return np.array(out)


def fwd_basis_stats(spec: FwdSpec, F, P):
    """Forward points and annualised basis measures."""
    z = -np.log(P(spec.T)) / spec.T
    return {"points": F - spec.S, "basis_pct": (F / spec.S - 1.0) * 100, "basis_ann_cc": np.log(F / spec.S) / spec.T,
            "zero_cc": z, "net_carry_cc": np.log(F / spec.S) / spec.T - z}


def replication_general(spec: FwdSpec, K, P, steps=4, path=None, pos=1):
    """Replicating portfolio of a long forward struck at K with known cash flows and the continuous carry.
    Date t_k = kT/steps.  Portfolio = n_t units of the asset  - n_t PV_t(remaining income) + n_t PV_t(remaining costs)
    - K P(t,T),  n_t = exp(c (T-t)).  Independent value: (F_t - K) P(t,T) with F_t re-computed from the formula.
    Cash flows that fall between two dates are taken into account through the PV of the *remaining* flows."""
    ts = np.linspace(0.0, spec.T, steps + 1)
    if path is None:
        path = [spec.S * np.exp(np.log(fwd_price(replace(spec, T=max(spec.T, 1e-9)), P) / spec.S) * t / spec.T) for t in ts]
    path = np.asarray(path, float)
    rows = {k: [] for k in ("S", "n", "asset", "inc", "cost", "loan", "port", "fwd")}
    for t, s in zip(ts, path):
        rem = spec.T - t
        Pt = lambda x, t=t: P(x + t) / P(t)       # discount function seen from t
        inc = pv_flows(spec.income, spec.T, Pt, t0=t) if rem > 1e-12 else 0.0
        cst = pv_flows(spec.costs, spec.T, Pt, t0=t) if rem > 1e-12 else 0.0
        n_t = np.exp(spec.carry * rem)
        PtT = Pt(rem) if rem > 1e-12 else 1.0
        spec_t = replace(spec, S=s, T=max(rem, 1e-12), income=tuple(_flows(spec.income, spec.T, t)), costs=tuple(_flows(spec.costs, spec.T, t)))
        F_t = fwd_price(spec_t, Pt) if rem > 1e-12 else s
        rows["S"].append(s)
        rows["n"].append(n_t)
        rows["asset"].append(n_t * s)
        rows["inc"].append(-n_t * inc)
        rows["cost"].append(n_t * cst)
        rows["loan"].append(-K * PtT)
        rows["port"].append(n_t * (s - inc + cst) - K * PtT)
        rows["fwd"].append((F_t - K) * PtT)
    df = pd.DataFrame(rows).T
    df.columns = [f"t={t:.2f}" for t in ts]
    sgn = -1.0 if pos == -1 else 1.0
    err = float(np.max(np.abs(np.array(rows["port"]) - np.array(rows["fwd"]))))
    for k in ("asset", "inc", "cost", "loan", "port", "fwd"):
        df.loc[k] *= sgn
    return df, {"max_abs_err": err, "ts": ts}
