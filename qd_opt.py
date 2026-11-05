"""Quant Desk - options engine: Black-Scholes-Merton, CRR lattice, Greeks, strategies, sensitivity, regime."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.special import ndtr
from scipy.optimize import brentq

_SQRT2PI = np.sqrt(2.0 * np.pi)


def N(x):
    """Standard normal CDF (scipy.special.ndtr: same values as norm.cdf, without the per-call overhead)."""
    return ndtr(x)


def n(x):
    """Standard normal PDF."""
    return np.exp(-0.5 * np.square(x)) / _SQRT2PI


# ------------------------------------------------------------------------------- BSM
def _d(S, K, r, q, sig, T):
    sq = sig * np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sig ** 2) * T) / sq
    return d1, d1 - sq


def bsm(S, K, r, q, sig, T, cp="call"):
    """Price. cp: 'call'|'put'. Handles T->0 (intrinsic)."""
    S, K, sig, T = map(lambda x: np.asarray(x, float), (S, K, sig, T))
    s = 1 if cp == "call" else -1
    with np.errstate(all="ignore"):
        d1, d2 = _d(S, K, r, q, sig, T)
        px = s * (S * np.exp(-q * T) * N(s * d1) - K * np.exp(-r * T) * N(s * d2))
    intrinsic = np.maximum(s * (S - K), 0.0)
    out = np.where(T <= 1e-10, intrinsic, px)
    return float(out) if out.ndim == 0 else out


def greeks(S, K, r, q, sig, T, cp="call"):
    """Analytic Greeks. theta per day, vega & rho per 1 vol-pt / 1 pct-pt, plus vanna, volga, charm (per day)."""
    s = 1 if cp == "call" else -1
    d1, d2 = _d(S, K, r, q, sig, T)
    eq, er, sq = np.exp(-q * T), np.exp(-r * T), np.sqrt(T)
    delta = s * eq * N(s * d1)
    gamma = eq * n(d1) / (S * sig * sq)
    vega = S * eq * n(d1) * sq
    theta = (-S * eq * n(d1) * sig / (2 * sq) - s * r * K * er * N(s * d2) + s * q * S * eq * N(s * d1))
    rho = s * K * T * er * N(s * d2)
    vanna = -eq * n(d1) * d2 / sig
    volga = vega * d1 * d2 / sig
    charm = s * q * eq * N(s * d1) - eq * n(d1) * (2 * (r - q) * T - d2 * sig * sq) / (2 * T * sig * sq)
    return {"delta": delta, "gamma": gamma, "vega": vega / 100, "theta": theta / 365, "rho": rho / 100,
            "vanna": vanna / 100, "volga": volga / 1e4, "charm": charm / 365}


def implied_vol(price, S, K, r, q, T, cp="call"):
    s = 1 if cp == "call" else -1
    lo = max(s * (S * np.exp(-q * T) - K * np.exp(-r * T)), 0.0)
    if price <= lo + 1e-12 or T <= 0:
        return np.nan
    try:
        return brentq(lambda v: bsm(S, K, r, q, v, T, cp) - price, 1e-4, 6.0, xtol=1e-10)
    except ValueError:
        return np.nan


def implied_vol_vec(price, S, K, r, q, T, cp):
    """Vectorised implied vol (bisection on [1e-4, 6]); NaN where the scalar implied_vol would return NaN."""
    price, K = np.asarray(price, float), np.asarray(K, float)
    sgn = np.where(np.asarray(cp) == "call", 1.0, -1.0)
    lo_b = np.maximum(sgn * (S * np.exp(-q * T) - K * np.exp(-r * T)), 0.0)
    ok = (price > lo_b + 1e-12) & (T > 0)

    def f(v):
        with np.errstate(all="ignore"):
            d1 = (np.log(S / K) + (r - q + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
            d2 = d1 - v * np.sqrt(T)
            return sgn * (S * np.exp(-q * T) * N(sgn * d1) - K * np.exp(-r * T) * N(sgn * d2)) - price

    lo, hi = np.full(price.shape, 1e-4), np.full(price.shape, 6.0)
    flo, fhi = f(lo), f(hi)
    ok &= (np.sign(flo) * np.sign(fhi) <= 0) & np.isfinite(flo) & np.isfinite(fhi)
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        left = np.sign(fm) == np.sign(flo)
        lo = np.where(left, mid, lo)
        hi = np.where(left, hi, mid)
    return np.where(ok, 0.5 * (lo + hi), np.nan)


# ------------------------------------------------------------------------------ CRR
def crr(S, K, r, q, sig, T, cp="call", steps=10, american=False):
    """Cox-Ross-Rubinstein lattice. Returns dict with price, node arrays (list per layer), delta/gamma/theta at nodes."""
    dt = T / steps
    u = np.exp(sig * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    if not (0 < p < 1):
        raise ValueError("Tree is arbitrageable: increase steps or volatility (p outside (0,1)).")
    disc = np.exp(-r * dt)
    s = 1 if cp == "call" else -1
    spot = [S * u ** (np.arange(i, -1, -1)) * d ** (np.arange(0, i + 1)) for i in range(steps + 1)]
    val = [None] * (steps + 1)
    exer = [None] * (steps + 1)
    val[steps] = np.maximum(s * (spot[steps] - K), 0.0)
    exer[steps] = np.zeros(steps + 1, bool)
    for i in range(steps - 1, -1, -1):
        cont = disc * (p * val[i + 1][:-1] + (1 - p) * val[i + 1][1:])
        if american:
            iv = np.maximum(s * (spot[i] - K), 0.0)
            exer[i] = iv > cont + 1e-12
            val[i] = np.maximum(cont, iv)
        else:
            exer[i] = np.zeros(i + 1, bool)
            val[i] = cont
    delta = [None] * steps
    for i in range(steps):
        delta[i] = (val[i + 1][:-1] - val[i + 1][1:]) / (spot[i + 1][:-1] - spot[i + 1][1:])
    gamma = [None] * max(steps - 1, 0)
    for i in range(steps - 1):
        up, dn = delta[i + 1][:-1], delta[i + 1][1:]
        gamma[i] = (up - dn) / (0.5 * (spot[i + 2][:-2] - spot[i + 2][2:]))
    out = {"price": float(val[0][0]), "spot": spot, "value": val, "delta": delta, "gamma": gamma, "exercise": exer,
           "u": u, "d": d, "p": p, "dt": dt}
    if steps >= 2:
        out["delta0"] = float(delta[0][0])
        out["gamma0"] = float(gamma[0][0])
        out["theta0"] = float((val[2][1] - val[0][0]) / (2 * dt) / 365)   # centre node of layer 2 has S=S0
    else:
        out["delta0"], out["gamma0"], out["theta0"] = float(delta[0][0]), np.nan, np.nan
    return out


def crr_convergence(S, K, r, q, sig, T, cp="call", american=False, steps_list=range(1, 11)):
    bs = bsm(S, K, r, q, sig, T, cp)
    rows = []
    for k in steps_list:
        try:
            t = crr(S, K, r, q, sig, T, cp, k, american)
            rows.append({"steps": k, "price": t["price"], "delta": t["delta0"], "gamma": t["gamma0"], "err": t["price"] - bs})
        except ValueError:
            rows.append({"steps": k, "price": np.nan, "delta": np.nan, "gamma": np.nan, "err": np.nan})
    return pd.DataFrame(rows), bs


# --------------------------------------------------------------------------- positions
@dataclass
class Leg:
    cp: str            # call | put | stock
    K: float
    qty: float         # signed contracts (+ long / - short)
    T: float
    sig: float
    mult: float = 100.0
    premium: float | None = None   # per unit; None -> BSM fair value at inception
    divs: tuple = ()               # discrete cash dividends ((t_years_from_now, D), ...): escrowed model S* = S - PV(divs <= T)


def pv_divs(divs, r, T, elapsed=0.0):
    """PV (at time `elapsed`) of discrete dividends paid in (elapsed, T] (times measured from the original t=0)."""
    return float(sum(D * np.exp(-r * (t - elapsed)) for t, D in divs if elapsed < t <= T + 1e-12))


def shift_leg(L, dT):
    """Leg seen `dT` years later: shorter life, dividends already paid are dropped, remaining ones re-timed."""
    return Leg(L.cp, L.K, L.qty, max(L.T - dT, 1e-4), L.sig, L.mult, L.premium,
               tuple((t - dT, D) for t, D in L.divs if t > dT + 1e-12))


def _s_eff(L, S, r, elapsed=0.0):
    """Escrowed-dividend spot for a leg: S - PV(dividends before its expiry).  Identity when the leg has no dividends."""
    if not L.divs:
        return S
    return np.maximum(np.asarray(S, float) - pv_divs(L.divs, r, L.T, elapsed), 1e-9)


def leg_price(leg, S, r, q, T=None, sig=None):
    T = leg.T if T is None else T
    sig = leg.sig if sig is None else sig
    if leg.cp == "stock":
        return S
    return bsm(_s_eff(leg, S, r, leg.T - T), leg.K, r, q, sig, T, leg.cp)


def position_value(legs, S, r, q, dT=0.0, dsig=0.0):
    """Mark-to-model value of the whole position (cash terms)."""
    tot = 0.0
    for L in legs:
        T = max(L.T - dT, 0.0)
        tot += L.qty * L.mult * leg_price(L, S, r, q, T, max(L.sig + dsig, 1e-4))
    return tot


def entry_cost(legs, S0, r, q):
    return sum(L.qty * L.mult * (L.premium if L.premium is not None else leg_price(L, S0, r, q)) for L in legs)


def position_greeks(legs, S, r, q):
    """Greeks of the whole position. S may be a scalar (floats returned) or an array (arrays returned)."""
    keys = ["delta", "gamma", "vega", "theta", "rho", "vanna", "volga", "charm"]
    arr = np.ndim(S) > 0
    zero = np.zeros(np.shape(S)) if arr else 0.0
    tot = {k: zero for k in keys}
    for L in legs:
        if L.cp == "stock":
            tot["delta"] = tot["delta"] + L.qty * L.mult
            continue
        g = greeks(_s_eff(L, S, r), L.K, r, q, L.sig, L.T, L.cp)
        if L.divs:   # escrowed model: S* = S - PV(divs) drifts at r*PV(divs) as time passes -> extra theta term -Delta*r*PVD
            g = dict(g)
            g["theta"] = g["theta"] - g["delta"] * r * pv_divs(L.divs, r, L.T) / 365.0
        for k in keys:
            tot[k] = tot[k] + L.qty * L.mult * (np.asarray(g[k], float) if arr else float(g[k]))
    return tot


def payoff_at_expiry(legs, Sgrid, S0, r, q):
    """P&L at the FIRST expiry. Legs that expire later are still alive and valued with BSM on their remaining life."""
    Sg = np.asarray(Sgrid, float)
    opt = [L.T for L in legs if L.cp != "stock"]
    Tm = min(opt) if opt else 0.0
    tot = np.zeros_like(Sg)
    for L in legs:
        if L.cp == "stock":
            pay = Sg
        elif L.T - Tm < 1e-9:
            pay = np.maximum(Sg - L.K, 0) if L.cp == "call" else np.maximum(L.K - Sg, 0)
        else:
            pay = O_bsm_grid(Sg, L, r, q, L.T - Tm)
        tot += L.qty * L.mult * pay
    return tot - entry_cost(legs, S0, r, q)


def O_bsm_grid(Sg, L, r, q, T):
    S_ = _s_eff(L, np.maximum(np.asarray(Sg, float), 1e-9), r, L.T - T)
    return np.asarray(bsm(S_, L.K, r, q, L.sig, T, L.cp), float)


def pnl_curve(legs, Sgrid, S0, r, q, dT=0.0, dsig=0.0):
    c0 = entry_cost(legs, S0, r, q)
    return np.asarray(position_value(legs, np.asarray(Sgrid, float), r, q, dT, dsig), float) - c0


def strategy_stats(legs, S0, r, q, span=0.6):
    """Max profit / loss / breakevens at expiry over a +-span spot range (unbounded flagged)."""
    Sg = np.linspace(0.0, S0 * (1 + span) * 1.5, 4001)
    pl = payoff_at_expiry(legs, Sg, S0, r, q)
    be = Sg[:-1][np.sign(pl[:-1]) * np.sign(pl[1:]) < 0]
    slope_hi = (pl[-1] - pl[-2]) / (Sg[-1] - Sg[-2])
    thr = 0.05 * sum(abs(L.qty) * L.mult for L in legs)       # tail slope above 5% of gross size = unbounded
    return {"cost": entry_cost(legs, S0, r, q),
            "max_profit": np.inf if slope_hi > thr else float(pl.max()),
            "max_loss": -np.inf if slope_hi < -thr else float(pl.min()),
            "breakevens": [float(b) for b in be]}


def attribution(legs, S0, S1, r, q, dT, dsig):
    """Taylor P&L split using Greeks at S0 (delta, gamma, vega, theta) + residual vs full revaluation."""
    g = position_greeks(legs, S0, r, q)
    dS = S1 - S0
    parts = {"delta": g["delta"] * dS, "gamma": 0.5 * g["gamma"] * dS ** 2, "vega": g["vega"] * dsig * 100,
             "theta": g["theta"] * dT * 365}
    full = position_value(legs, S1, r, q, dT, dsig) - position_value(legs, S0, r, q)
    parts["residual"] = full - sum(parts.values())
    parts["total"] = full
    return parts


def breakeven_move(legs, S0, r, q):
    """Daily 1-sigma move (in S) that gamma P&L needs to offset theta: |theta| = 0.5 Gamma dS^2."""
    g = position_greeks(legs, S0, r, q)
    if g["gamma"] <= 1e-12 or g["theta"] >= 0:
        return np.nan
    return float(np.sqrt(2 * -g["theta"] / g["gamma"]))


# ------------------------------------------------------------------------ sensitivity
def greek_surface(legs, name, S0, r, q, Sgrid, Tgrid):
    """Greek of the position as function of spot and time-to-go (T shifted from now)."""
    M = np.zeros((len(Tgrid), len(Sgrid)))
    Sg = np.asarray(Sgrid, float)
    for i, dT in enumerate(Tgrid):
        sh = [shift_leg(L, dT) for L in legs]
        M[i, :] = position_greeks(sh, Sg, r, q)[name]
    return M


def pnl_heatmap(legs, S0, r, q, spot_moves, vol_moves, dT=0.0):
    """Rows = vol shift (pts), columns = spot move (%). Full revaluation."""
    c0 = position_value(legs, S0, r, q)
    S1 = S0 * (1 + np.asarray(spot_moves, float))
    return np.array([np.asarray(position_value(legs, S1, r, q, dT, dv), float) - c0 for dv in vol_moves])


def ladder(legs, S0, r, q, moves):
    c0 = position_value(legs, S0, r, q)
    rows = []
    for m in moves:
        S1 = S0 * (1 + m)
        g = position_greeks(legs, S1, r, q)
        rows.append({"move": m, "S": S1, "pnl": position_value(legs, S1, r, q) - c0, "delta": g["delta"], "gamma": g["gamma"],
                     "vega": g["vega"]})
    return pd.DataFrame(rows)


def smile_from_chain(chain, S, r, q, T):
    """chain: DataFrame[strike, mid, cp] -> adds iv column."""
    c = chain.copy()
    c["iv"] = implied_vol_vec(c["mid"].to_numpy(float), S, c["strike"].to_numpy(float), r, q, T, c["cp"].to_numpy())
    return c


# ----------------------------------------------------------------------------- regime
def realized_vol(prices, window=21):
    r = np.log(np.asarray(prices, float))
    r = np.diff(r)
    return float(np.std(r[-window:], ddof=1) * np.sqrt(252)) if len(r) >= window else np.nan


def detect_regime(prices, iv_atm, skew=None):
    """Classify the market from price history + ATM IV (+ optional put-call skew in vol pts).
    Returns dict: vol_state (rich/cheap/fair), trend (up/down/range), skew_state, tags."""
    p = np.asarray(prices, float)
    rv = realized_vol(p, 21)
    rv_long = realized_vol(p, min(len(p) - 1, 126))
    ratio = iv_atm / rv if rv and rv > 0 else np.nan
    vol_state = "rich" if ratio > 1.2 else "cheap" if ratio < 0.85 else "fair"
    ret60 = p[-1] / p[max(-61, -len(p))] - 1
    sma50 = p[-50:].mean() if len(p) >= 50 else p.mean()
    trend = "up" if (p[-1] > sma50 and ret60 > 0.03) else "down" if (p[-1] < sma50 and ret60 < -0.03) else "range"
    skew_state = "none"
    if skew is not None and not np.isnan(skew):
        skew_state = "steep" if skew > 0.05 else "flat" if skew < 0.01 else "normal"
    return {"rv": rv, "rv_long": rv_long, "iv": iv_atm, "iv_rv": ratio, "vol_state": vol_state, "trend": trend,
            "ret60": ret60, "skew": skew, "skew_state": skew_state}


# --------------------------------------------------------------------------- strategies
def build_strategy(name, S, T, sig, qty=1, mult=100.0, width=0.05, wing=0.10):
    """Library of defined strategies around spot S (strikes rounded to 1)."""
    k = lambda m: float(np.round(S * m))
    L = lambda cp, K, qt: Leg(cp, K, qt * qty, T, sig, mult)
    A = k(1.0)
    lo, hi = k(1 - width), k(1 + width)
    wlo, whi = k(1 - wing), k(1 + wing)
    lib = {
        "long_call": [L("call", A, 1)], "long_put": [L("put", A, 1)],
        "covered_call": [L("stock", 0, 1), L("call", hi, -1)],
        "protective_put": [L("stock", 0, 1), L("put", lo, 1)],
        "collar": [L("stock", 0, 1), L("put", lo, 1), L("call", hi, -1)],
        "bull_call_spread": [L("call", A, 1), L("call", hi, -1)],
        "bear_put_spread": [L("put", A, 1), L("put", lo, -1)],
        "long_straddle": [L("call", A, 1), L("put", A, 1)],
        "short_straddle": [L("call", A, -1), L("put", A, -1)],
        "long_strangle": [L("call", hi, 1), L("put", lo, 1)],
        "short_strangle": [L("call", hi, -1), L("put", lo, -1)],
        "iron_condor": [L("put", wlo, 1), L("put", lo, -1), L("call", hi, -1), L("call", whi, 1)],
        "butterfly": [L("call", lo, 1), L("call", A, -2), L("call", hi, 1)],
        "risk_reversal": [L("call", hi, 1), L("put", lo, -1)],
        "put_ratio_spread": [L("put", A, 1), L("put", wlo, -2)],
        "calendar": [Leg("call", A, -1 * qty, T, sig, mult), Leg("call", A, 1 * qty, T * 2, sig, mult)],
    }
    return lib[name]


STRATEGY_VIEW = {  # name: (view, vol_exposure)
    "long_call": ("bullish", "long vol"), "long_put": ("bearish", "long vol"),
    "covered_call": ("mildly bullish / income", "short vol"), "protective_put": ("long, hedged", "long vol"),
    "collar": ("long, hedged cheaply", "neutral vol"), "bull_call_spread": ("moderately bullish", "~neutral vol"),
    "bear_put_spread": ("moderately bearish", "~neutral vol"), "long_straddle": ("big move either way", "long vol"),
    "short_straddle": ("pinned near spot", "short vol"), "long_strangle": ("big move either way, cheaper", "long vol"),
    "short_strangle": ("range-bound", "short vol"), "iron_condor": ("range-bound, capped risk", "short vol"),
    "butterfly": ("pin at a level", "short vol"), "risk_reversal": ("bullish, funded by skew", "skew"),
    "put_ratio_spread": ("mildly bearish / vol-sell skew", "short vol, tail risk"),
    "calendar": ("quiet now, move later", "long term / short front vol"),
}


def recommend(regime, top=3):
    """Rule-based ranking: maps (vol_state, trend, skew) to strategies, with plain-language rationale keys."""
    v, t, sk = regime["vol_state"], regime["trend"], regime["skew_state"]
    sc = {k: 0.0 for k in STRATEGY_VIEW}
    why = {k: [] for k in STRATEGY_VIEW}

    def add(k, w, tag):
        sc[k] += w
        why[k].append(tag)

    if v == "rich":
        for k in ("iron_condor", "short_strangle", "covered_call", "butterfly", "put_ratio_spread"):
            add(k, 2, "iv_rich")
        for k in ("long_straddle", "long_strangle", "long_call", "long_put"):
            add(k, -2, "iv_rich")
    elif v == "cheap":
        for k in ("long_straddle", "long_strangle", "long_call", "long_put", "protective_put", "calendar"):
            add(k, 2, "iv_cheap")
        for k in ("short_straddle", "short_strangle", "iron_condor"):
            add(k, -2, "iv_cheap")
    else:
        for k in ("bull_call_spread", "bear_put_spread", "collar", "butterfly"):
            add(k, 1, "iv_fair")
    if t == "up":
        for k in ("bull_call_spread", "risk_reversal", "covered_call", "long_call"):
            add(k, 2, "trend_up")
        for k in ("long_put", "bear_put_spread"):
            add(k, -2, "trend_up")
    elif t == "down":
        for k in ("bear_put_spread", "long_put", "protective_put", "collar"):
            add(k, 2, "trend_down")
        for k in ("long_call", "bull_call_spread", "risk_reversal"):
            add(k, -2, "trend_down")
    else:
        for k in ("iron_condor", "butterfly", "short_strangle", "calendar", "covered_call"):
            add(k, 1.5, "range")
        for k in ("long_straddle", "long_strangle"):
            add(k, 0.5, "range")
    if sk == "steep":
        for k in ("risk_reversal", "put_ratio_spread", "covered_call"):
            add(k, 1, "skew_steep")
        for k in ("protective_put",):
            add(k, -1, "skew_steep")
    elif sk == "flat":
        for k in ("protective_put", "collar"):
            add(k, 1, "skew_flat")
    order = sorted(sc, key=lambda k: -sc[k])[:top]
    return [{"name": k, "score": sc[k], "why": why[k], "view": STRATEGY_VIEW[k][0], "vol": STRATEGY_VIEW[k][1]} for k in order]


# ======================================================================================================
# Extended models & analytics
# ======================================================================================================
def black76(F, K, r, sig, T, cp="call"):
    """Black (1976) option on a forward / futures price F, discounted at r:  e^{-rT}[F N(d1) - K N(d2)]  (call).
    Identical to BSM with S = F and q = r."""
    return bsm(F, K, r, r, sig, T, cp)


def garman_kohlhagen(S, K, rd, rf, sig, T, cp="call"):
    """Garman-Kohlhagen (1983) FX option: BSM with the foreign rate as the continuous yield (S in domestic per foreign)."""
    return bsm(S, K, rd, rf, sig, T, cp)


def rho_black76(F, K, r, sig, T, cp="call"):
    """Black-76 rho when F is held fixed:  dV/dr = -T V  (per 1 pct-pt = /100)."""
    return -T * black76(F, K, r, sig, T, cp) / 100.0


def greeks_ext(S, K, r, q, sig, T, cp="call"):
    """Higher-order & auxiliary Greeks (closed forms, Haug, 'Complete Guide to Option Pricing Formulas', ch.7; Hull ch.19).
    Time derivatives are calendar (T falls). Units: speed per $^-1, zomma per vol-pt (1/100), color per day, veta per vol-pt per day, ultima per vol-pt^3,
    dual delta dV/dK, dual gamma d2V/dK2, epsilon dV/dq per 1 pct-pt, lambda = elasticity (Delta*S/V), prob_itm = N(s d2)."""
    s = 1 if cp == "call" else -1
    d1, d2 = _d(S, K, r, q, sig, T)
    sq = np.sqrt(T)
    eq, er = np.exp(-q * T), np.exp(-r * T)
    phi = n(d1)
    gamma = eq * phi / (S * sig * sq)
    vega = S * eq * phi * sq
    price = bsm(S, K, r, q, sig, T, cp)
    delta = s * eq * N(s * d1)
    speed = -gamma / S * (d1 / (sig * sq) + 1.0)
    zomma = gamma * (d1 * d2 - 1.0) / sig
    # calendar-time derivatives (sign convention of `charm`: time passes, T falls) = minus the time-to-expiry derivative
    color = eq * phi / (2 * S * T * sig * sq) * (2 * q * T + 1.0 + d1 * (2 * (r - q) * T - d2 * sig * sq) / (sig * sq))
    veta = S * eq * phi * sq * (q + (r - q) * d1 / (sig * sq) - (1.0 + d1 * d2) / (2 * T))
    ultima = -vega / sig ** 2 * (d1 * d2 * (1.0 - d1 * d2) + d1 ** 2 + d2 ** 2)
    return {"speed": speed, "zomma": zomma / 100, "color": color / 365, "veta": veta / 100 / 365, "ultima": ultima / 1e6,
            "dual_delta": -s * er * N(s * d2), "dual_gamma": er * n(d2) / (K * sig * sq),
            "epsilon": -s * T * S * eq * N(s * d1) / 100, "lambda": (delta * S / price) if price > 1e-12 else np.nan,
            "prob_itm": N(s * d2)}


def implied_forward(call, put, K, r, T):
    """Put-call parity (European):  C - P = e^{-rT}(F - K)  =>  F = K + e^{rT}(C - P)."""
    return K + np.exp(r * T) * (call - put)


def parity_table(chain, S, r, T):
    """Per-strike implied forward and implied continuous yield q (F = S e^{(r-q)T}) from matched call / put mids."""
    c = chain[chain.cp == "call"].set_index("strike")["mid"]
    p = chain[chain.cp == "put"].set_index("strike")["mid"]
    k = c.index.intersection(p.index)
    if len(k) == 0:
        return pd.DataFrame(columns=["strike", "call", "put", "F_imp", "q_imp"])
    F = implied_forward(c.loc[k].to_numpy(float), p.loc[k].to_numpy(float), k.to_numpy(float), r, T)
    with np.errstate(all="ignore"):
        q_imp = r - np.log(F / S) / T
    return pd.DataFrame({"strike": k.to_numpy(float), "call": c.loc[k].to_numpy(float), "put": p.loc[k].to_numpy(float), "F_imp": F, "q_imp": q_imp})


def price_bounds(S, K, r, q, T, cp="call"):
    """No-arbitrage bounds for a European option (Merton 1973): lower = max(s(S e^{-qT} - K e^{-rT}), 0); upper = S e^{-qT} (call) / K e^{-rT} (put)."""
    s = 1 if cp == "call" else -1
    lo = max(s * (S * np.exp(-q * T) - K * np.exp(-r * T)), 0.0)
    hi = S * np.exp(-q * T) if cp == "call" else K * np.exp(-r * T)
    return lo, hi


def crr_divs(S, K, r, q, sig, T, cp="call", steps=200, american=False, divs=()):
    """CRR price with discrete cash dividends (Hull ch.21 / Wilmott): the tree is built on S* = S - PV(remaining dividends)
    (volatility applies to S*); at every node the actual stock price S* + PV(remaining dividends at that date) is used for exercise."""
    divs = [(float(t), float(D)) for t, D in divs if 0 < t <= T + 1e-12]
    dt = T / steps
    u = np.exp(sig * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    if not (0 < p < 1):
        raise ValueError("Tree is arbitrageable: increase steps or volatility (p outside (0,1)).")
    disc = np.exp(-r * dt)
    sgn = 1 if cp == "call" else -1
    pvd = lambda t: sum(D * np.exp(-r * (ti - t)) for ti, D in divs if ti > t + 1e-12)
    S0s = S - pvd(0.0)
    if S0s <= 0:
        raise ValueError("Dividends exceed the spot price.")
    i_ = np.arange(steps + 1)
    Sn = S0s * u ** (steps - 2 * i_)
    val = np.maximum(sgn * (Sn + pvd(T) - K), 0.0)           # pvd(T)=0 : dividends at T are already excluded from S*
    for k in range(steps - 1, -1, -1):
        j = np.arange(k + 1)
        Sk = S0s * u ** (k - 2 * j)
        cont = disc * (p * val[:-1] + (1 - p) * val[1:])
        if american:
            ex = np.maximum(sgn * (Sk + pvd(k * dt) - K), 0.0)
            cont = np.maximum(cont, ex)
        val = cont
    return float(val[0])


def position_rho_b76(legs, F, r, q=None):
    """Black-76 rho of a position (F fixed): sum of -T * V per option, per 1 pct-pt of r."""
    return float(sum(L.qty * L.mult * rho_black76(F, L.K, r, L.sig, L.T, L.cp) for L in legs if L.cp != "stock"))
