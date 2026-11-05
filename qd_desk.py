"""Quant Desk - trading-desk tools on top of the curve engine (qd_rates):
bumped-curve overlays, the DV01 family (par-quote, zero-rate bucket, forward bucket, PV01, gamma), swap book,
hedge solver, DV01-neutral curve trades, FRA / futures convexity (Ho-Lee).

Sign convention (same as qd_rates): a DV01 is the P&L for a 1 bp FALL in rates, so it is positive for a receive-fixed swap.
References: Tuckman & Serrat, Fixed Income Securities (ch. 5-6, key-rate durations / partial DV01);
Ho (1992) 'Key rate durations'; Hull, OFOD ch. 4/7 (FRA, swap valuation) and ch. 6 (Ho-Lee convexity adjustment);
Andersen & Piterbarg, Interest Rate Modeling, vol. 1 (bucketed sensitivities).
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

import qd_rates as R


# ------------------------------------------------------------------------------ bumped curves
class OverlayCurve(R.Curve):
    """Base curve plus an additive shift of ln DF:  ln DF'(t) = ln DF(t) + dl(t).  No re-bootstrap (instant)."""

    def __init__(self, base: R.Curve, dl):
        self.base, self._dl = base, dl
        self.method, self.freq, self.fallback = base.method, base.freq, base.fallback
        self.instruments, self.tmax = base.instruments, base.tmax

    def lndf(self, t):
        t = np.asarray(t, float)
        return self.base.lndf(t) + self._dl(t)


def _hat(nodes, k):
    """Piecewise-linear hat on `nodes`: 1 at nodes[k], 0 at the neighbours, flat outside the first / last node."""
    x = np.asarray(nodes, float)
    y = np.zeros(len(x))
    y[k] = 1.0
    return lambda t: np.interp(np.asarray(t, float), x, y)       # np.interp is flat outside [x0, xn]


def zero_bucket_curve(base: R.Curve, nodes, k, bp):
    """Shift the cc zero rate by `bp` basis points with a hat centred on nodes[k]  (Δ ln DF = -Δz(t)·t)."""
    h = _hat(nodes, k)
    d = bp / 1e4
    return OverlayCurve(base, lambda t: -d * h(t) * np.asarray(t, float))


def parallel_zero_curve(base: R.Curve, bp):
    d = bp / 1e4
    return OverlayCurve(base, lambda t: -d * np.asarray(t, float))


def fwd_bucket_curve(base: R.Curve, edges, k, bp):
    """Shift the instantaneous forward rate by `bp` on [edges[k], edges[k+1]) (last bucket open-ended)."""
    a = edges[k]
    b = edges[k + 1] if k + 1 < len(edges) else np.inf
    d = bp / 1e4
    return OverlayCurve(base, lambda t: -d * np.clip(np.minimum(np.asarray(t, float), b) - a, 0.0, None))


# ------------------------------------------------------------------------------ DV01 family
def _central(fn, make, bp):
    return (fn(make(-bp)) - fn(make(+bp))) / 2.0          # P&L for a `bp` fall (positive = gains when rates fall)


def zero_dv01(curve, fn, bp=1.0):
    return (fn(parallel_zero_curve(curve, -bp)) - fn(parallel_zero_curve(curve, bp))) / 2.0


def zero_bucket_dv01(curve, fn, nodes=None, bp=1.0):
    nodes = np.asarray(nodes if nodes is not None else [i.tenor for i in curve.instruments], float)
    return np.array([_central(fn, lambda s, k=k: zero_bucket_curve(curve, nodes, k, s), bp) for k in range(len(nodes))])


def fwd_bucket_dv01(curve, fn, edges, bp=1.0):
    edges = np.asarray(edges, float)
    return np.array([_central(fn, lambda s, k=k: fwd_bucket_curve(curve, edges, k, s), bp) for k in range(len(edges))])


def gamma_zero(curve, fn, bp=1.0):
    """Second derivative along a parallel cc-zero shift, expressed in $ per bp^2:  PV(+b)+PV(-b)-2PV(0), b = bp."""
    return fn(parallel_zero_curve(curve, bp)) + fn(parallel_zero_curve(curve, -bp)) - 2.0 * fn(curve)


def fixed_leg_pv01(curve, notional, T, freq, start=0.0):
    """Annuity PV01: change in the fixed-leg PV for a 1 bp change in the fixed rate (analytic, = N A 1e-4)."""
    return notional * curve.annuity(T, freq, start) * 1e-4


def pv_ladder(curve, fn, shocks_bp, method_rebuild=True):
    """Full-revaluation P&L for parallel PAR-quote shocks (re-bootstrap) next to the delta and delta+gamma estimates."""
    base = fn(curve)
    n = len(curve.instruments)
    full = np.array([R._pv_shocked(curve, fn, np.full(n, s)) - base for s in shocks_bp])
    d = R.parallel_dv01(curve, fn)
    g = R._pv_shocked(curve, fn, np.full(n, 1.0)) + R._pv_shocked(curve, fn, np.full(n, -1.0)) - 2 * base
    s = np.asarray(shocks_bp, float)
    return pd.DataFrame({"shock_bp": s, "full": full, "delta": -d * s, "delta_gamma": -d * s + 0.5 * g * s ** 2}), d, g


# ------------------------------------------------------------------------------ swap book
@dataclass
class Trade:
    side: int            # +1 receive fixed, -1 pay fixed
    notional: float
    tenor: float         # years from start
    fixed: float         # decimal
    start: float = 0.0   # forward start (years)
    label: str = ""


def trade_pv(curve, tr: Trade, freq):
    return R.swap_pv(curve, tr.notional, tr.fixed, tr.tenor, freq, tr.side == 1, tr.start)


def book_pv(curve, trades, freq):
    return float(sum(trade_pv(curve, t, freq) for t in trades))


def book_summary(curve, trades, freq):
    """PV, parallel par-DV01 (re-bootstrapped), zero-bucket DV01 and forward-bucket DV01 for a book of swaps."""
    f = lambda c: book_pv(c, trades, freq)
    nodes = [i.tenor for i in curve.instruments]
    edges = [0.0, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
    edges = [e for e in edges if e < curve.tmax - 1e-9]
    out = {"pv": f(curve), "par_dv01": R.parallel_dv01(curve, f), "zero_dv01": zero_dv01(curve, f),
           "zero_buckets": zero_bucket_dv01(curve, f), "fwd_buckets": fwd_bucket_dv01(curve, f, edges),
           "gamma": gamma_zero(curve, f), "nodes": nodes, "edges": edges}
    return out


# ------------------------------------------------------------------------------ hedging
def par_swap_unit(curve, T, freq):
    """A receive-fixed par swap with unit notional, struck at today's par rate (PV = 0)."""
    K = curve.par_rate(T, freq)
    return lambda c: R.swap_pv(c, 1.0, K, T, freq, True)


def hedge_matrix(curve, tenors, freq, nodes=None):
    nodes = np.asarray(nodes if nodes is not None else [i.tenor for i in curve.instruments], float)
    cols = [zero_bucket_dv01(curve, par_swap_unit(curve, T, freq), nodes) for T in tenors]
    return np.column_stack(cols)


def solve_hedge(g, H, ridge=0.0):
    """Notionals x (receive-fixed positive) minimising || g + H x ||_2 over the zero buckets.
    Exactly neutral when H is square and non-singular; otherwise least squares (min-norm if under-determined)."""
    g = np.asarray(g, float)
    if ridge > 0:
        A = np.vstack([H, np.sqrt(ridge) * np.eye(H.shape[1])])
        b = np.r_[-g, np.zeros(H.shape[1])]
        x = np.linalg.lstsq(A, b, rcond=None)[0]
    else:
        x = np.linalg.lstsq(H, -g, rcond=None)[0]
    res = g + H @ x
    return x, res


# ------------------------------------------------------------------------------ DV01-neutral curve trades
def dv01_neutral_spread(curve, T_short, T_long, notional_long, freq):
    """Steepener: receive T_short, pay T_long, DV01 neutral (PV01 = N * annuity * 1bp).  Returns notionals (signed)."""
    a_s, a_l = curve.annuity(T_short, freq), curve.annuity(T_long, freq)
    n_short = notional_long * a_l / a_s
    return {"N_short": n_short, "N_long": notional_long, "A_short": a_s, "A_long": a_l,
            "pv01_short": n_short * a_s * 1e-4, "pv01_long": notional_long * a_l * 1e-4}


def dv01_neutral_fly(curve, T1, T2, T3, notional_belly, freq, w1=0.5):
    """Butterfly: receive the belly T2 and pay the wings (T1, T3) with DV01 weights w1 / (1-w1) of the belly DV01."""
    a1, a2, a3 = (curve.annuity(x, freq) for x in (T1, T2, T3))
    d2 = notional_belly * a2
    n1, n3 = w1 * d2 / a1, (1 - w1) * d2 / a3
    return {"N1": n1, "N2": notional_belly, "N3": n3, "pv01": d2 * 1e-4, "A": (a1, a2, a3)}


# ------------------------------------------------------------------------------ FRA / convexity
def fra_rate(curve, t1, t2):
    """Simple forward rate for [t1, t2]:  (DF1/DF2 - 1)/(t2 - t1)."""
    return float((curve.df_at(t1) / curve.df_at(t2) - 1.0) / (t2 - t1))


def fra_value(curve, notional, K, t1, t2, pay_fixed=True):
    """FRA settled in arrears at t2: PV = N tau (F - K) DF(t2) for the payer of K (receives the floating rate)."""
    tau = t2 - t1
    v = notional * tau * (fra_rate(curve, t1, t2) - K) * curve.df_at(t2)
    return v if pay_fixed else -v


def ho_lee_convexity(sigma, t1, t2):
    """Hull (OFOD ch.6): forward rate = futures rate - 0.5 sigma^2 t1 t2  (sigma: annual normal vol of the short rate, decimal)."""
    return 0.5 * sigma ** 2 * t1 * t2


# ------------------------------------------------------------------------------ what-if helpers
def apply_bumps(instruments, bumps_bp):
    b = np.asarray(bumps_bp, float) / 1e4
    return [R.Instrument(i.tenor, i.kind, i.quote + b[k], i.label) for k, i in enumerate(instruments)]


def compare_curves(base: R.Curve, new: R.Curve, tenors):
    t = np.asarray(tenors, float)
    rows = {"t": t}
    rows["d_zero"] = (new.zero(t, "cc") - base.zero(t, "cc")) * 1e4
    rows["d_par"] = np.array([(new.par_rate(x) - base.par_rate(x)) * 1e4 if x >= 1 / base.freq else np.nan for x in t])
    rows["d_fwd"] = (new.inst_forward(t) - base.inst_forward(t)) * 1e4
    return pd.DataFrame(rows)


def factor_bumps(tenors, level, slope, curv):
    """Level / slope / curvature what-if in bp: short = level - slope/2, long = level + slope/2, belly = curv."""
    return R.scenario_bumps(tenors, level - slope / 2.0, level + slope / 2.0, curv)
