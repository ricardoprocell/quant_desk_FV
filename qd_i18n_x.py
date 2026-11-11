"""Quant Desk - EN / ES strings for the desk-level features (forward builder, curve desk tools, options models & tools)."""
X = {
 # ---------------------------------------------------------------- forward builder
 "fb_sub": ("Build any forward from scratch: pick the asset class, set carry, cash flows, discounting, frictions and risk.",
            "Construye cualquier forward desde cero: elige la clase de activo, el carry, los flujos, el descuento, las fricciones y el riesgo."),
 "fb_asset": ("Asset class", "Clase de activo"),
 "fb_a_equity": ("Equity (dividends)", "Acción (dividendos)"), "fb_a_index": ("Index (yield)", "Índice (yield)"), "fb_a_fx": ("FX", "FX"),
 "fb_a_commodity": ("Commodity", "Commodity"), "fb_a_bond": ("Bond (coupons)", "Bono (cupones)"),
 "fb_qty": ("Units / notional", "Unidades / nocional"), "fb_qty_help": ("Number of units of the underlying (shares, index multiplier, FX notional, barrels…).", "Número de unidades del subyacente (acciones, multiplicador, nocional FX, barriles…)."),
 "fb_days": ("Maturity (days)", "Vencimiento (días)"), "fb_days_help": ("Calendar days to delivery; years = days/365.", "Días naturales a la entrega; años = días/365."),
 "fb_q_equity": ("Dividend yield q (%)", "Dividend yield q (%)"), "fb_q_index": ("Dividend yield q (%)", "Dividend yield q (%)"),
 "fb_q_fx": ("Foreign rate r_f (%)", "Tasa extranjera r_f (%)"), "fb_q_commodity": ("Other yield / lease rate (%)", "Otro yield / lease rate (%)"),
 "fb_q_bond": ("Running yield (%)", "Yield corriente (%)"),
 "fb_q_help": ("Continuous yield paid to the holder, annual cc. For FX it is the foreign interest rate (covered interest parity).", "Rendimiento continuo que recibe el tenedor, anual cc. En FX es la tasa extranjera (paridad cubierta de tasas)."),
 "fb_b": ("Borrow fee b (%)", "Costo de préstamo b (%)"), "fb_b_help": ("Securities-lending fee earned by the holder / paid by a short seller (cc). Lowers the forward like a yield.", "Comisión de préstamo del activo que gana el tenedor / paga el vendedor en corto (cc). Baja el forward como un yield."),
 "fb_disc": ("Discounting", "Descuento"), "fb_d_curve": ("Curve", "Curva"), "fb_d_flat": ("Flat rate", "Tasa plana"),
 "fb_rflat": ("Flat rate r (% cc)", "Tasa plana r (% cc)"), "fb_spread": ("Spread over discount (bp)", "Spread sobre el descuento (pb)"),
 "fb_spread_help": ("Funding spread added to the discount rate (cc). Positive = you finance above the curve.", "Spread de fondeo sumado a la tasa de descuento (cc). Positivo = te fondeas por encima de la curva."),
 "fb_inc_title": ("Discrete cash income (dividends, coupons)", "Ingresos discretos (dividendos, cupones)"), "fb_inc_hdr": ("Income received by the holder", "Ingresos que recibe el tenedor"),
 "fb_cost_title": ("Discrete costs (storage, insurance)", "Costos discretos (almacenaje, seguro)"), "fb_cost_hdr": ("Costs paid by the holder", "Costos que paga el tenedor"),
 "fb_inc_help": ("Generate N equal payments or edit the table directly. PV is taken with the same discount function. Flows after maturity are ignored.", "Genera N pagos iguales o edita la tabla. El VP usa la misma función de descuento. Los flujos posteriores al vencimiento se ignoran."),
 "fb_cost_help": ("Paid at the dates below (e.g. warehouse rent). Raises the forward: F = (S − PV(income) + PV(costs))·e^{cT}/P(T).", "Se pagan en las fechas indicadas (p. ej. renta de bodega). Suben el forward: F = (S − VP(ingresos) + VP(costos))·e^{cT}/P(T)."),
 "fb_n": ("How many", "Cuántos"), "fb_amt": ("Each (amount)", "Monto c/u"), "fb_first": ("First (day)", "Primero (día)"), "fb_every": ("Every (days)", "Cada (días)"),
 "fb_gen": ("Generate schedule", "Generar calendario"), "fb_day": ("Day", "Día"), "fb_amount": ("Amount", "Monto"),
 "fb_late": ("{n} cash flow(s) fall after maturity and are ignored.", "{n} flujo(s) caen después del vencimiento y se ignoran."),
 "fb_neg_adj": ("The PV of income exceeds the spot price: S − PV(income) ≤ 0. Check the dividend schedule.", "El VP de los ingresos supera el spot: S − VP(ingresos) ≤ 0. Revisa el calendario de dividendos."),
 "fb_have_mkt": ("I have a market forward quote", "Tengo una cotización de mercado"), "fb_have_mkt_help": ("Off: the market forward equals the model price. On: enter the quote to see implied parameters and arbitrage.", "Apagado: el forward de mercado es el del modelo. Encendido: ingresa la cotización para ver parámetros implícitos y arbitraje."),
 "fb_vol": ("Volatility (%)", "Volatilidad (%)"), "fb_vol_help": ("Used for the risk view only (VaR, P&L distribution). A forward itself has no vol exposure.", "Solo para la vista de riesgo (VaR, distribución de P&L). El forward en sí no tiene exposición a vol."),
 "fb_points": ("Forward points", "Puntos forward"), "fb_vs_spot": ("vs spot", "vs spot"), "fb_basis_ann": ("Basis (ann.)", "Base (anual)"),
 "fb_netcarry": ("Net carry", "Carry neto"), "fb_vs_zero": ("zero {z}%", "cero {z}%"), "fb_pv_inc": ("PV income − costs", "VP ingresos − costos"), "fb_pv_inc_sub": ("price units", "unidades de precio"),
 "fb_t_price": ("Pricing", "Valuación"), "fb_t_risk": ("Risk", "Riesgo"), "fb_t_term": ("Term structure", "Estructura temporal"), "fb_t_repl": ("Replication", "Replicación"), "fb_t_arb": ("Arbitrage band", "Banda de arbitraje"),
 "fb_w_spot": ("Spot", "Spot"), "fb_w_inc": ("− PV income", "− VP ingresos"), "fb_w_cost": ("+ PV costs", "+ VP costos"), "fb_w_carry": ("Carry u−y−q−b", "Carry u−y−q−b"), "fb_w_fin": ("Financing", "Financiamiento"), "fb_w_F": ("Forward", "Forward"),
 "fb_build_title": ("How the forward is built", "Cómo se construye el forward"), "fb_pay_title": ("Payoff and mark-to-market", "Payoff y valor a mercado"),
 "fb_impl_title": ("What the market quote implies", "Qué implica la cotización de mercado"), "fb_param": ("Quantity", "Magnitud"), "fb_implied": ("Implied", "Implícito"), "fb_input": ("Input", "Supuesto"), "fb_unit": ("Unit", "Unidad"),
 "fb_i_carry": ("Net carry c = u−y−q−b", "Carry neto c = u−y−q−b"), "fb_i_y": ("Convenience yield y", "Convenience yield y"), "fb_i_q": ("Yield q", "Yield q"), "fb_i_u": ("Storage cost u", "Costo de almacenaje u"),
 "fb_i_b": ("Borrow fee b", "Costo de préstamo b"), "fb_i_repo": ("Financing rate (cc)", "Tasa de financiamiento (cc)"), "fb_i_spread": ("Spread over discount", "Spread sobre el descuento"), "fb_i_pvinc": ("PV income − costs (price units)", "VP ingresos − costos (unid. de precio)"),
 "fb_impl_note": ("Each line solves for ONE unknown holding the others at your inputs (F = (S − PV inc + PV costs)·e^{cT}/P(T)). With the model price they reproduce your inputs.", "Cada línea despeja UNA incógnita dejando las demás en tus supuestos (F = (S − VP ing. + VP costos)·e^{cT}/P(T)). Con el precio del modelo reproducen tus supuestos."),
 "fb_parallel": ("parallel zero", "cero paralelo"), "fb_stor01": ("Storage 1bp", "Almacenaje 1pb"), "fb_b01": ("Borrow 1bp", "Préstamo 1pb"),
 "fb_grid_title": ("Mark-to-market: spot × rates", "Valor a mercado: spot × tasas"), "fb_rate_shift": ("Parallel zero shift (bp)", "Cambio paralelo de ceros (pb)"),
 "fb_grid_hover": ("Spot %{x:+.0f}% · rates %{y:+.0f}bp<br>ΔMTM $%{z:,.0f}", "Spot %{x:+.0f}% · tasas %{y:+.0f}pb<br>ΔMTM $%{z:,.0f}"),
 "fb_conf": ("VaR confidence", "Confianza del VaR"), "fb_hz": ("VaR horizon (days)", "Horizonte del VaR (días)"),
 "fb_lambda": ("Risk premium on the underlying (% p.a.)", "Prima de riesgo del subyacente (% anual)"), "fb_lambda_help": ("0 = risk-neutral: E[S_T] = F. Positive values shift the expected terminal price up.", "0 = neutral al riesgo: E[S_T] = F. Valores positivos suben el precio esperado a vencimiento."),
 "fb_dist": ("P&L at maturity", "P&L a vencimiento"), "fb_dist_title": ("P&L distribution at maturity (lognormal)", "Distribución del P&L a vencimiento (lognormal)"), "fb_exp": ("expected", "esperado"), "fb_pl_T": ("P&L at delivery ($)", "P&L a la entrega ($)"),
 "fb_var": ("VaR {c}% · {d}d", "VaR {c}% · {d}d"), "fb_var_sub": ("loss in MTM, full revaluation", "pérdida en MTM, revaluación completa"),
 "fb_ev": ("Expected P&L", "P&L esperado"), "fb_ev_sub": ("at delivery", "a la entrega"), "fb_pwin": ("P(P&L > 0)", "P(P&L > 0)"), "fb_pwin_sub": ("at delivery", "a la entrega"),
 "fb_sd_T": ("Std dev of P&L", "Desv. est. del P&L"), "fb_sd_sub": ("at delivery", "a la entrega"),
 "fb_risk_note": ("A forward has no optionality: its risk is linear in spot (Δ) and small in rates — here ρ ≈ ${rho} per bp and ${q} per bp of yield. The distribution only reflects the volatility you typed.", "El forward no tiene opcionalidad: su riesgo es lineal en el spot (Δ) y pequeño en tasas — aquí ρ ≈ ${rho} por pb y ${q} por pb de yield. La distribución solo refleja la volatilidad que escribiste."),
 "fb_this": ("This forward", "Este forward"), "fb_price_axis": ("Forward price", "Precio forward"), "fb_zero": ("Zero rate (cc)", "Tasa cero (cc)"), "fb_carry_cc": ("Net carry c", "Carry neto c"),
 "fb_basis_title": ("Annualised basis vs rates", "Base anualizada vs tasas"), "fb_csv": ("Download term structure (CSV)", "Descargar estructura temporal (CSV)"),
 "fb_r_S": ("Spot S_t", "Spot S_t"), "fb_r_n": ("Units held n_t = e^{c(T−t)}", "Unidades n_t = e^{c(T−t)}"), "fb_r_asset": ("Asset n_t·S_t", "Activo n_t·S_t"), "fb_r_inc": ("− n_t·PV(remaining income)", "− n_t·VP(ingresos restantes)"),
 "fb_r_cost": ("+ n_t·PV(remaining costs)", "+ n_t·VP(costos restantes)"), "fb_r_loan": ("Loan −K·P(t,T)", "Préstamo −K·P(t,T)"), "fb_r_port": ("Portfolio value", "Valor del portafolio"), "fb_r_fwd": ("Forward value (F_t−K)·P(t,T)", "Valor del forward (F_t−K)·P(t,T)"),
 "fb_repl_help": ("The portfolio is rebuilt with the formula, F_t is recomputed from the cash flows still to come — the two rows must match on every path.", "El portafolio se reconstruye con la fórmula y F_t se recalcula con los flujos que faltan — las dos filas deben coincidir en cualquier trayectoria."),
 "fb_fr_hs": ("Half bid/ask on spot (bp)", "Medio bid/ask del spot (pb)"), "fb_fr_hs_help": ("Buying spot costs S(1+h); selling spot yields S(1−h).", "Comprar spot cuesta S(1+h); vender spot rinde S(1−h)."),
 "fb_fr_sb": ("Borrow spread (bp)", "Spread al pedir prestado (pb)"), "fb_fr_sb_help": ("Cash-and-carry financing: curve + this spread.", "Financiamiento del cash-and-carry: curva + este spread."),
 "fb_fr_sl": ("Lend spread (bp)", "Spread al prestar (pb)"), "fb_fr_sl_help": ("Reverse cash-and-carry proceeds earn curve − this spread.", "El producto del reverse cash-and-carry gana curva − este spread."),
 "fb_fr_fee": ("Fixed cost / unit", "Costo fijo / unidad"), "fb_fr_fee_help": ("Round-trip commissions and fees in price units.", "Comisiones por ida y vuelta en unidades de precio."),
 "fb_f_dn": ("Lower bound", "Cota inferior"), "fb_f_up": ("Upper bound", "Cota superior"), "fb_inside": ("Inside the band", "Dentro de la banda"),
 "fb_gap_fair": ("Market − fair", "Mercado − justo"), "fb_net_profit": ("Net arbitrage profit", "Ganancia neta de arbitraje"), "fb_band_w": ("Band width", "Ancho de banda"), "fb_band_sub": ("no-arbitrage corridor", "corredor sin arbitraje"),
 "fb_arb_note": ("With frictions there is no single fair price but a corridor: inside it no arbitrage survives costs. Outside it the profit shown is what is left after financing spreads, bid/ask and fees.", "Con fricciones no hay un precio justo único sino un corredor: dentro de él ningún arbitraje sobrevive a los costos. Fuera, la ganancia mostrada es lo que queda tras spreads de fondeo, bid/ask y comisiones."),

 # ---------------------------------------------------------------- options fixes
 "crr500": ("Lattice (500)", "Árbol (500)"),
 "lat_vs_bsm": ("The 10-step lattice is didactic: with so few steps its price jumps from node to node when spot moves, so a $1 move in spot will not change it by Δ. Black-Scholes is the exact reference; the 500-step lattice shows the convergence.",
                "El árbol de 10 pasos es didáctico: con tan pocos pasos su precio salta de nodo en nodo cuando se mueve el spot, así que $1 de spot no lo cambia en Δ. Black-Scholes es la referencia exacta; el árbol de 500 pasos muestra la convergencia."),
 "bd_unit_delta": ("Δ per option", "Δ por opción"), "bd_total": ("Total", "Total"),
 "bd_units": ("Position columns are in cash terms (contracts × multiplier): Δ = shares-equivalent, Γ = change in Δ per $1, Vega = $ per vol point, Θ = $ per day. A short put has positive Δ and negative Vega.",
              "Las columnas de posición están en efectivo (contratos × multiplicador): Δ = equivalente en acciones, Γ = cambio de Δ por $1, Vega = $ por punto de vol, Θ = $ por día. Una put corta tiene Δ positiva y Vega negativa."),

 # ---------------------------------------------------------------- curve desk tools
 "dk_title": ("Desk tools", "Herramientas de mesa"), "dk_sub": ("What-if on market quotes · DV01 family · swap book & hedge · FRA & convexity", "What-if sobre cotizaciones · familia de DV01 · libro de swaps y cobertura · FRA y convexidad"),
 "dk_t_whatif": ("Market what-if", "What-if de mercado"), "dk_t_ladder": ("DV01 ladder", "Escalera de DV01"), "dk_t_book": ("Book & hedge", "Libro y cobertura"), "dk_t_fra": ("FRA & futures", "FRA y futuros"),
 "dk_level": ("Level (bp)", "Nivel (pb)"), "dk_level_help": ("Parallel move of every par quote.", "Movimiento paralelo de todas las cotizaciones par."),
 "dk_slope": ("Slope (bp)", "Pendiente (pb)"), "dk_slope_help": ("Long end minus short end: +20 raises the long end by 10bp and lowers the short end by 10bp.", "Extremo largo menos corto: +20 sube el largo 10pb y baja el corto 10pb."),
 "dk_curv": ("Curvature (bp)", "Curvatura (pb)"), "dk_curv_help": ("Moves the belly against the wings.", "Mueve el vientre contra las puntas."),
 "dk_s_zero": ("Zero", "Cero"), "dk_s_par": ("Par", "Par"), "dk_s_fwd": ("Forward", "Forward"),
 "dk_pillar": ("Bump individual quotes (bp)", "Mover cotizaciones individuales (pb)"), "dk_bump": ("Bump (bp)", "Cambio (pb)"),
 "dk_whatif_idle": ("Move a slider (or type a bump per pillar) to see the curve, the risk-section swap and the key spreads reprice.", "Mueve un control (o escribe un cambio por pilar) para ver cómo se revalúan la curva, el swap de la sección de riesgo y los spreads clave."),
 "dk_d2": ("Δ 2Y zero", "Δ cero 2A"), "dk_d10": ("Δ 10Y zero", "Δ cero 10A"), "dk_swap_pnl": ("Swap P&L", "P&L del swap"),
 "dk_base": ("Base", "Base"), "dk_shocked": ("Shocked", "Con shock"), "dk_delta_title": ("Change vs base (bp)", "Cambio vs base (pb)"),
 "dk_apply": ("Apply to quotes", "Aplicar a cotizaciones"), "dk_apply_help": ("Writes the shocked rates into the market-quotes table (Reset restores market).", "Escribe las tasas con shock en la tabla de cotizaciones (Reset restaura el mercado)."),
 "dk_apply_off": ("Clear the pasted OIS text to apply bumps to the quotes table.", "Borra el texto OIS pegado para aplicar los cambios a la tabla de cotizaciones."),
 "dk_dv_type": ("Bucket definition", "Definición de buckets"), "dk_dv_par": ("Par quotes", "Cotizaciones par"), "dk_dv_zero": ("Zero rates", "Tasas cero"), "dk_dv_fwd": ("Forward rates", "Tasas forward"),
 "dk_dv_help_par": ("Bump one market quote, re-bootstrap the whole curve (key-rate DV01, Ho 1992). What a trader hedges with swaps.", "Mueve una cotización de mercado y re-construye la curva (DV01 por tramo, Ho 1992). Lo que se cubre con swaps."),
 "dk_dv_help_zero": ("Bump the continuously-compounded zero rate with a triangular hat around each pillar. Buckets add up to the parallel zero DV01.", "Mueve la tasa cero cc con un triángulo alrededor de cada pilar. Los buckets suman el DV01 cero paralelo."),
 "dk_dv_help_fwd": ("Bump the instantaneous forward on each time bucket (partial durations). Buckets add up to the parallel zero DV01.", "Mueve la forward instantánea en cada tramo (duraciones parciales). Los buckets suman el DV01 cero paralelo."),
 "dk_bump_size": ("Bump size", "Tamaño del shock"), "dk_k_par": ("DV01 par", "DV01 par"), "dk_k_par_s": ("parallel, re-bootstrapped", "paralelo, re-construido"),
 "dk_k_zero": ("DV01 zero", "DV01 cero"), "dk_k_zero_s": ("parallel zero shift", "shift paralelo de ceros"), "dk_annuity": ("(annuity)", "(anualidad)"), "dk_pv01_s": ("N · A · 1bp", "N · A · 1pb"),
 "dk_gamma": ("Convexity", "Convexidad"), "dk_gamma_s": ("$ per bp² (PV″)", "$ por pb² (VP″)"), "dk_dur": ("Mod. duration", "Duración mod."), "dk_dur_s": ("years of PV01/notional", "años de PV01/nocional"),
 "dk_sum": ("Σ {s}", "Σ {s}"), "dk_full": ("Full revaluation", "Revaluación completa"), "dk_delta_only": ("Delta only", "Solo delta"), "dk_delta_gamma": ("Delta + gamma", "Delta + gamma"),
 "dk_shock_bp": ("Parallel shock (bp)", "Shock paralelo (pb)"), "dk_ladder_title": ("P&L vs parallel shock", "P&L vs shock paralelo"), "dk_bucket": ("Bucket", "Tramo"),
 "dk_ladder_note": ("Convexity matters: for a +100bp shock the full revaluation is ${g} while delta + gamma estimates ${dg}; the remainder is higher-order terms.", "La convexidad importa: para un shock de +100pb la revaluación completa da ${g} y delta + gamma estima ${dg}; el resto son términos de orden superior."),
 "dk_book_title": ("Swap book", "Libro de swaps"), "dk_book_reset": ("Reset book", "Reiniciar libro"), "dk_fixed_blank": ("Empty = struck at today's par rate", "Vacío = a la tasa par de hoy"),
 "dk_start": ("Start (y)", "Inicio (a)"), "dk_book_empty": ("Add at least one swap to the book (tenor + start must stay inside the curve).", "Agrega al menos un swap al libro (plazo + inicio deben quedar dentro de la curva)."), "dk_trades": ("trade(s)", "operación(es)"),
 "dk_hedge_title": ("Hedge the book with par swaps", "Cobertura del libro con swaps par"), "dk_hedge_with": ("Hedge instruments", "Instrumentos de cobertura"),
 "dk_ridge": ("Regularisation", "Regularización"), "dk_ridge_off": ("none", "ninguna"), "dk_ridge_help": ("Penalises large notionals when instruments overlap (ridge). None = exact least squares.", "Penaliza nocionales grandes cuando los instrumentos se traslapan (ridge). Ninguna = mínimos cuadrados exactos."),
 "dk_hedge_pick": ("Pick at least one hedge instrument.", "Elige al menos un instrumento de cobertura."),
 "dk_res_zero": ("Residual DV01 zero", "DV01 cero residual"), "dk_after": ("after hedge", "tras cobertura"), "dk_before": ("Book", "Libro"),
 "dk_res_par": ("Residual DV01 par", "DV01 par residual"), "dk_after_par": ("re-bootstrapped check", "verificación con re-construcción"),
 "dk_res_norm": ("Risk removed", "Riesgo eliminado"), "dk_res_norm_s": ("size of the bucket vector", "norma del vector de buckets"), "dk_gross": ("Gross hedge notional", "Nocional bruto de cobertura"), "dk_gross_s": ("sum of |N|", "suma de |N|"),
 "dk_hedge_chart": ("Zero-rate bucket DV01: before and after", "DV01 por bucket de tasa cero: antes y después"),
 "dk_instr": ("Instrument", "Instrumento"), "dk_notional_signed": ("Notional", "Nocional"), "dk_action": ("Action", "Acción"),
 "dk_hedge_note": ("Solves min‖g + H·x‖ over the zero-rate buckets. Positive notional = receive fixed.", "Resuelve min‖g + H·x‖ sobre los buckets de tasa cero. Nocional positivo = recibir fija."),
 "dk_ct_title": ("DV01-neutral curve trades", "Trades de curva neutrales en DV01"), "dk_ct_kind": ("Trade", "Operación"), "dk_ct_steep": ("Steepener", "Steepener"), "dk_ct_flat": ("Flattener", "Flattener"), "dk_ct_fly": ("Butterfly", "Mariposa"),
 "dk_short_leg": ("Short tenor", "Plazo corto"), "dk_long_leg": ("Long tenor", "Plazo largo"), "dk_wing1": ("Short wing", "Punta corta"), "dk_belly": ("Belly", "Vientre"), "dk_wing2": ("Long wing", "Punta larga"),
 "dk_ct_notional": ("Notional of the long leg / belly", "Nocional del tramo largo / vientre"), "dk_ct_order": ("Choose increasing tenors: short < long (or wing < belly < wing).", "Elige plazos crecientes: corto < largo (o punta < vientre < punta)."),
 "dk_ct_move": ("Spread move", "Cambio del spread"), "dk_ct_move_fly": ("Belly move", "Cambio del vientre"),
 "dk_ct_note": ("Net PV01 ${net}/bp by construction. Zero-rate DV01 ${zdv}/bp: small but non-zero because par PV01 and zero DV01 weight the curve differently.", "PV01 neto ${net}/pb por construcción. DV01 de tasas cero ${zdv}/pb: pequeño pero no nulo porque el PV01 par y el DV01 cero ponderan la curva distinto."),
 "dk_fra_start": ("FRA starts in (y)", "El FRA inicia en (a)"), "dk_fra_len": ("Accrual period", "Periodo de acumulación"), "dk_fra_k": ("Contract rate (%)", "Tasa contratada (%)"),
 "dk_fra_range": ("The FRA end date falls beyond the curve.", "El fin del FRA queda fuera de la curva."), "dk_fra_pay": ("Pay fixed (long FRA)", "Paga fija (FRA largo)"), "dk_fra_rec": ("Receive fixed", "Recibe fija"),
 "dk_fra_fair": ("Fair FRA rate", "Tasa FRA justa"), "dk_fra_fair_s": ("simple, from the curve", "simple, de la curva"), "dk_fra_diff": ("Fair − contract", "Justa − contratada"), "dk_fra_diff_s": ("bp", "pb"),
 "dk_cx_title": ("Futures convexity adjustment (Ho-Lee)", "Ajuste de convexidad de futuros (Ho-Lee)"), "dk_cx_sigma": ("Short-rate normal vol σ (bp/yr)", "Vol normal de la tasa corta σ (pb/año)"),
 "dk_cx_help": ("Hull: forward rate = futures rate − ½σ²·t₁·t₂. 100bp = 1% normal vol.", "Hull: tasa forward = tasa de futuros − ½σ²·t₁·t₂. 100pb = 1% de vol normal."),
 "dk_cx_chart": ("Convexity bias by expiry (bp)", "Sesgo de convexidad por vencimiento (pb)"), "dk_cx_exp": ("Expiry", "Vencimiento"), "dk_cx_fwd": ("Forward (cc)", "Forward (cc)"), "dk_cx_adj": ("Adjustment", "Ajuste"), "dk_cx_fut": ("Implied futures", "Futuro implícito"),
 "dk_cx_note": ("Futures settle daily, so gains arrive when rates are favourable to reinvest: the futures rate sits above the forward rate. The effect grows with t₁·t₂, which is why long-dated Eurodollar/SOFR strips need it when building a curve.", "Los futuros se liquidan a diario, así que las ganancias llegan cuando conviene reinvertirlas: la tasa del futuro queda sobre la forward. El efecto crece con t₁·t₂, por eso las tiras largas de Eurodólar/SOFR lo necesitan al construir la curva."),
 "dk_refs": ("Methodology & references", "Metodología y referencias"),
 "dk_refs_body": ("""**Sign convention.** DV01 = P&L for a 1 bp *fall* in rates (positive for a receive-fixed swap), central differences.

**Par (key-rate) DV01** bumps one market quote and re-bootstraps the full curve; the sum over pillars equals the parallel par DV01 to first order (Ho 1992; Tuckman & Serrat ch. 6). **Zero-rate buckets** shift the cc zero rate with hats that sum to one, so the buckets add exactly to the parallel zero DV01. **Forward buckets** shift the instantaneous forward on disjoint intervals (partial durations).

**Annuity PV01** = N·Σαᵢ·DF(tᵢ)·1bp is the exact sensitivity of the fixed-leg PV to the *fixed rate*. **Convexity** is PV(+b)+PV(−b)−2PV(0) in $ per bp². **Hedge solver:** x = argmin‖g + Hx‖₂ over the zero buckets with H the bucket DV01 of unit par swaps. **FRA:** PV = N·τ·(F−K)·DF(t₂), F = (DF(t₁)/DF(t₂)−1)/τ. **Convexity:** forward = futures − ½σ²t₁t₂ (Ho-Lee, Hull).

*References:* Hull, Options, Futures and Other Derivatives (ch. 4, 6, 7); Ho (1992) “Key rate durations”, J. Fixed Income 2(2); Ho & Lee (1986) J. Finance 41(5); Tuckman & Serrat, Fixed Income Securities (3rd ed.).""",
 """**Convención de signo.** DV01 = P&L por una *baja* de 1 pb en tasas (positivo para un swap que recibe fija), diferencias centrales.

**DV01 par (por tramo)** mueve una cotización de mercado y re-construye toda la curva; la suma de pilares iguala el DV01 par paralelo a primer orden (Ho 1992; Tuckman & Serrat cap. 6). Los **buckets de tasa cero** mueven la cero cc con triángulos que suman uno, así que suman exactamente el DV01 cero paralelo. Los **buckets forward** mueven la forward instantánea en intervalos disjuntos (duraciones parciales).

**PV01 de anualidad** = N·Σαᵢ·DF(tᵢ)·1pb es la sensibilidad exacta del VP de la pata fija a la *tasa fija*. **Convexidad** es VP(+b)+VP(−b)−2VP(0) en $ por pb². **Solver de cobertura:** x = argmin‖g + Hx‖₂ sobre los buckets cero con H el DV01 por bucket de swaps par unitarios. **FRA:** VP = N·τ·(F−K)·DF(t₂), F = (DF(t₁)/DF(t₂)−1)/τ. **Convexidad:** forward = futuro − ½σ²t₁t₂ (Ho-Lee, Hull).

*Referencias:* Hull, Options, Futures and Other Derivatives (cap. 4, 6, 7); Ho (1992) “Key rate durations”, J. Fixed Income 2(2); Ho & Lee (1986) J. Finance 41(5); Tuckman & Serrat, Fixed Income Securities (3a ed.)."""),
 # ---------------------------------------------------------------- options models / tools
 "om_model": ("Pricing model", "Modelo de valuación"), "om_m_bsm": ("Black-Scholes-Merton", "Black-Scholes-Merton"), "om_m_b76": ("Black-76 (futures)", "Black-76 (futuros)"), "om_m_gk": ("Garman-Kohlhagen (FX)", "Garman-Kohlhagen (FX)"),
 "om_help_bsm": ("Stock or index with a continuous dividend yield q, plus optional discrete dividends below.", "Acción o índice con dividend yield continuo q, más dividendos discretos opcionales abajo."),
 "om_help_b76": ("Option on a forward / futures price F: price = e^{−rT}[F·N(d₁) − K·N(d₂)]. Equivalent to BSM with S = F and q = r; ρ = −T·V.", "Opción sobre un precio forward / futuro F: precio = e^{−rT}[F·N(d₁) − K·N(d₂)]. Equivale a BSM con S = F y q = r; ρ = −T·V."),
 "om_help_gk": ("FX option: BSM with the foreign rate r_f as the continuous yield; spot in domestic per foreign currency.", "Opción FX: BSM con la tasa extranjera r_f como yield continuo; spot en moneda local por extranjera."),
 "om_fwd_px": ("Forward / futures price F", "Precio forward / futuro F"), "om_rf": ("Foreign rate r_f (%)", "Tasa extranjera r_f (%)"),
 "om_div_title": ("Discrete dividends (escrowed model)", "Dividendos discretos (modelo escrowed)"), "om_div_hdr": ("Cash dividends before expiry", "Dividendos en efectivo antes del vencimiento"),
 "om_div_help": ("S* = S − PV(dividends before expiry) enters Black-Scholes. Use either these or the continuous yield q, not both. American + dividends uses a dividend-adjusted lattice.", "S* = S − VP(dividendos antes del vencimiento) entra a Black-Scholes. Usa estos o el yield continuo q, no ambos. American + dividendos usa un árbol ajustado por dividendos."),
 "om_mark_smile": ("Mark vols to smile", "Marcar vols a la sonrisa"), "om_mark_smile_help": ("Sets each option's vol to the market implied vol at its strike (OTM smile).", "Pone la vol de cada opción en la vol implícita de mercado de su strike (sonrisa OTM)."),
 "v_tools": ("Tools", "Herramientas"),
 "om_iv_title": ("Implied-volatility calculator", "Calculadora de volatilidad implícita"), "om_iv_price": ("Option price", "Precio de la opción"), "om_iv": ("Implied vol", "Vol implícita"), "om_iv_sub": ("Brent root", "raíz de Brent"),
 "om_bounds": ("No-arb bounds", "Cotas sin arbitraje"), "om_iv_bad": ("The price is outside the no-arbitrage range [{lo}, {hi}]: no volatility reproduces it.", "El precio está fuera del rango sin arbitraje [{lo}, {hi}]: ninguna volatilidad lo reproduce."),
 "om_iv_note": ("Uses the current spot, rate, yield and the typed strike / days. European exercise.", "Usa el spot, tasa, yield actuales y el strike / días escritos. Ejercicio europeo."),
 "om_par_title": ("Put-call parity: implied forward", "Paridad put-call: forward implícito"), "om_F_imp": ("Implied forward", "Forward implícito"), "om_F_sub": ("median of 5 strikes nearest spot", "mediana de los 5 strikes más cercanos"),
 "om_F_model": ("Model forward", "Forward del modelo"), "om_F_model_sub": ("S·e^{(r−q)T}", "S·e^{(r−q)T}"), "om_q_imp": ("Implied yield q", "Yield q implícito"), "om_q_imp_sub": ("r − ln(F/S)/T", "r − ln(F/S)/T"),
 "om_par_note": ("C − P = e^{−rT}(F − K) for European options, so every strike gives an estimate of F. A flat line = consistent chain; the gap to the model forward is the market-implied dividend / borrow.", "C − P = e^{−rT}(F − K) en opciones europeas, así que cada strike da un estimador de F. Una línea plana = cadena consistente; la brecha contra el forward del modelo es el dividendo / préstamo implícito del mercado."),
 "om_par_none": ("No matched call / put quotes in the chain.", "No hay cotizaciones call / put emparejadas en la cadena."),
 "om_gx_title": ("Full Greek sheet for one option (per unit)", "Hoja completa de griegas de una opción (por unidad)"), "om_gx_def": ("Meaning", "Significado"),
 "gx_delta": ("dV/dS", "dV/dS"), "gx_gamma": ("d²V/dS²", "d²V/dS²"), "gx_vega": ("dV/dσ per vol pt", "dV/dσ por punto de vol"), "gx_theta": ("dV/dt per calendar day", "dV/dt por día natural"), "gx_rho": ("dV/dr per 1 pct-pt", "dV/dr por 1 pp"),
 "gx_vanna": ("dΔ/dσ per vol pt", "dΔ/dσ por punto de vol"), "gx_volga": ("d²V/dσ² per vol pt²", "d²V/dσ² por punto de vol²"), "gx_charm": ("dΔ/dt per day", "dΔ/dt por día"),
 "gx_speed": ("dΓ/dS", "dΓ/dS"), "gx_zomma": ("dΓ/dσ per vol pt", "dΓ/dσ por punto de vol"), "gx_color": ("dΓ/dt per day", "dΓ/dt por día"), "gx_veta": ("dVega/dt per vol pt per day", "dVega/dt por punto de vol por día"), "gx_ultima": ("d³V/dσ³ per vol pt³", "d³V/dσ³ por punto de vol³"),
 "gx_dual_delta": ("dV/dK", "dV/dK"), "gx_dual_gamma": ("d²V/dK² (risk-neutral density × e^{−rT})", "d²V/dK² (densidad neutral al riesgo × e^{−rT})"), "gx_eps": ("dV/dq per 1 pct-pt (foreign rate in GK)", "dV/dq por 1 pp (tasa extranjera en GK)"),
 "gx_lambda": ("Elasticity Δ·S/V (leverage)", "Elasticidad Δ·S/V (apalancamiento)"), "gx_prob": ("Risk-neutral P(S_T in the money)", "P(S_T en el dinero) neutral al riesgo"),
 "om_export": ("Export", "Exportar"), "om_dl_pos": ("Download position & Greeks (CSV)", "Descargar posición y griegas (CSV)"),
 "om_refs": ("Methodology & references", "Metodología y referencias"),
 "om_refs_body": ("""**Black-Scholes-Merton** with continuous yield: C = S·e^{−qT}N(d₁) − K·e^{−rT}N(d₂), d₁ = [ln(S/K) + (r−q+σ²/2)T]/(σ√T), d₂ = d₁ − σ√T (Black & Scholes 1973; Merton 1973). **Black-76** sets S = F, q = r (Black 1976). **Garman-Kohlhagen** sets q = r_f (1983).

**Discrete dividends (escrowed):** S* = S − Σ Dᵢe^{−rtᵢ} over dividends before expiry; volatility applies to S*. As time passes S* drifts at r·PV(D), which adds the term −Δ·r·PV(D) to Θ. The American lattice prices on S* and adds the PV of the *remaining* dividends back at each node for the exercise test (Hull ch. 21).

**Greeks** are closed-form (Haug 2007, ch. 7) and were verified against finite differences: Δ, Γ, vega, Θ, ρ to 1e-6 relative; time derivatives are calendar (T falls). **Implied vol:** Brent root of BSM(σ) − price. **Parity:** F = K + e^{rT}(C − P). **Lattice:** Cox-Ross-Rubinstein (1979); with few steps the price is a jagged function of S — only large N converges to BSM.

*References:* Black & Scholes (1973) J. Political Economy 81(3); Merton (1973) Bell J. Econ. Mgmt. Sci. 4(1); Black (1976) J. Financial Economics 3; Garman & Kohlhagen (1983) J. Int. Money & Finance 2(3); Cox, Ross & Rubinstein (1979) J. Financial Economics 7(3); Haug, The Complete Guide to Option Pricing Formulas (2nd ed.); Hull, OFOD (ch. 15–21).""",
 """**Black-Scholes-Merton** con yield continuo: C = S·e^{−qT}N(d₁) − K·e^{−rT}N(d₂), d₁ = [ln(S/K) + (r−q+σ²/2)T]/(σ√T), d₂ = d₁ − σ√T (Black & Scholes 1973; Merton 1973). **Black-76** fija S = F, q = r (Black 1976). **Garman-Kohlhagen** fija q = r_f (1983).

**Dividendos discretos (escrowed):** S* = S − Σ Dᵢe^{−rtᵢ} sobre los dividendos antes del vencimiento; la volatilidad aplica a S*. Al pasar el tiempo S* deriva a r·VP(D), lo que añade el término −Δ·r·VP(D) a Θ. El árbol americano valúa sobre S* y suma el VP de los dividendos *restantes* en cada nodo para la prueba de ejercicio (Hull cap. 21).

**Griegas** en forma cerrada (Haug 2007, cap. 7), verificadas contra diferencias finitas: Δ, Γ, vega, Θ, ρ a 1e-6 relativo; las derivadas en el tiempo son calendario (T disminuye). **Vol implícita:** raíz de Brent de BSM(σ) − precio. **Paridad:** F = K + e^{rT}(C − P). **Árbol:** Cox-Ross-Rubinstein (1979); con pocos pasos el precio es una función irregular de S — solo N grande converge a BSM.

*Referencias:* Black & Scholes (1973) J. Political Economy 81(3); Merton (1973) Bell J. Econ. Mgmt. Sci. 4(1); Black (1976) J. Financial Economics 3; Garman & Kohlhagen (1983) J. Int. Money & Finance 2(3); Cox, Ross & Rubinstein (1979) J. Financial Economics 7(3); Haug, The Complete Guide to Option Pricing Formulas (2a ed.); Hull, OFOD (cap. 15–21)."""),
 # ---------------------------------------------------------------- forward methodology
 "fb_refs": ("Methodology & references", "Metodología y referencias"),
 "fb_refs_body": ("""**General forward:** F = (S − PV(income) + PV(costs))·e^{cT} / P(0,T), with net carry c = u − y − q − b and P the discount function (your curve or a flat rate, plus the funding spread). Special cases: known income F = (S−I)e^{rT}; yield F = S·e^{(r−q)T}; storage F = (S+U)e^{rT} or S·e^{(r+u)T}; convenience yield F = S·e^{(r+u−y)T}; FX F = S·e^{(r−r_f)T} (covered interest parity).

**Reproduce Hull:** $50 stock, flat r = 8% (cc), dividends 0.75 at 3, 6, 9 months, maturity 10 months → I = 2.162, F = 51.14 (maturity 304 days rounds to 51.13). AUD/USD 0.62, r = 7%, r_f = 5%, 2 years → 0.6453.

**Value:** V = (F − K)·P(0,T) per unit; Δ = e^{cT}; ρ, q-, u-, y-, b-sensitivities are central differences. **Implied parameters** invert one unknown at a time. **Band:** F_up = (S(1+h) − I + U)e^{cT}e^{s_b T}/P(T) + fee, F_dn = (S(1−h) − I + U)e^{cT}e^{−s_l T}/P(T) − fee. **Replication:** hold n_t = e^{c(T−t)} units, finance with a loan of K·P(t,T), net of the PV of the remaining cash flows.

*References:* Hull, Options, Futures and Other Derivatives (ch. 5); Cox, Ingersoll & Ross (1981) “The relation between forward prices and futures prices”, J. Financial Economics 9(4) (forward = futures under deterministic rates).""",
 """**Forward general:** F = (S − VP(ingresos) + VP(costos))·e^{cT} / P(0,T), con carry neto c = u − y − q − b y P la función de descuento (tu curva o una tasa plana, más el spread de fondeo). Casos particulares: ingreso conocido F = (S−I)e^{rT}; yield F = S·e^{(r−q)T}; almacenaje F = (S+U)e^{rT} o S·e^{(r+u)T}; convenience yield F = S·e^{(r+u−y)T}; FX F = S·e^{(r−r_f)T} (paridad cubierta de tasas).

**Reproducir a Hull:** acción de $50, r plana 8% (cc), dividendos de 0.75 a 3, 6 y 9 meses, vencimiento 10 meses → I = 2.162, F = 51.14 (con 304 días redondea a 51.13). AUD/USD 0.62, r = 7%, r_f = 5%, 2 años → 0.6453.

**Valor:** V = (F − K)·P(0,T) por unidad; Δ = e^{cT}; las sensibilidades a ρ, q, u, y, b son diferencias centrales. **Parámetros implícitos** despejan una incógnita a la vez. **Banda:** F_sup = (S(1+h) − I + U)e^{cT}e^{s_b T}/P(T) + costo, F_inf = (S(1−h) − I + U)e^{cT}e^{−s_l T}/P(T) − costo. **Replicación:** mantener n_t = e^{c(T−t)} unidades, financiadas con un préstamo de K·P(t,T), neto del VP de los flujos restantes.

*Referencias:* Hull, Options, Futures and Other Derivatives (cap. 5); Cox, Ingersoll & Ross (1981) “The relation between forward prices and futures prices”, J. Financial Economics 9(4) (forward = futuro con tasas deterministas)."""),
 "dk_csv": ("Download DV01 buckets (CSV)", "Descargar buckets de DV01 (CSV)"),
 "dk_fra_pv": ("FRA PV", "VP del FRA"),
 "fb_q01_equity": ("Div. yield 1bp", "Div. yield 1pb"), "fb_q01_index": ("Div. yield 1bp", "Div. yield 1pb"), "fb_q01_fx": ("r_f 1bp", "r_f 1pb"),
 "fb_q01_commodity": ("Lease rate 1bp", "Lease rate 1pb"), "fb_q01_bond": ("Yield 1bp", "Yield 1pb"),
 # ---------------------------------------------------------------- quick par-rate edit + position book
 "qa_title": ("Quick par-rate edit", "Edición rápida de tasas par"),
 "qa_help": ("Pick a quote, type the new rate or nudge it in bp. The curve re-bootstraps instantly.", "Elige una cotización, escribe la nueva tasa o muévela en pb. La curva se re-construye al instante."),
 "qa_pillar": ("Quote", "Cotización"), "qa_new": ("New rate (%)", "Nueva tasa (%)"), "qa_set": ("Set rate", "Fijar tasa"),
 "qa_bump": ("or shift this quote (bp)", "o mover esta cotización (pb)"), "qa_apply1": ("Shift", "Mover"),
 "qa_scope": ("Parallel shift applies to", "El desplazamiento paralelo aplica a"), "qa_s_par": ("Par swaps / bonds", "Swaps / bonos par"), "qa_s_all": ("All quotes", "Todas las cotizaciones"),
 "qa_shift": ("Parallel shift (bp)", "Desplazamiento paralelo (pb)"), "qa_apply": ("Apply shift", "Aplicar"),
 "qa_chg": ("Changes vs market", "Cambios vs mercado"), "qa_none": ("No changes: the curve equals the market.", "Sin cambios: la curva es la de mercado."),
 "pm_mode": ("When loading", "Al cargar"), "pm_replace": ("Replace", "Reemplazar"), "pm_combine": ("Combine", "Combinar"),
 "pm_mode_help": ("Replace: the strategy becomes the whole position (one at a time). Combine: it is added as a separate block next to what you already have.",
                  "Reemplazar: la estrategia pasa a ser toda la posición (una a la vez). Combinar: se agrega como bloque aparte junto a lo que ya tienes."),
 "apply_add": ("Add to position", "Agregar a la posición"),
 "pm_on": ("Active", "Activa"), "pm_on_help": ("Untick to take the leg out of every calculation without deleting it.", "Desmarca para sacar la pata de todos los cálculos sin borrarla."),
 "pm_grp": ("Strategy", "Estrategia"), "pm_title": ("Position book", "Libro de posición"), "pm_blocks": ("blocks", "bloques"), "pm_legs_on": ("legs active", "patas activas"),
 "pm_legs": ("legs", "patas"), "pm_active": ("active", "activo"), "pm_paused": ("paused", "en pausa"),
 "pm_solo": ("Only this", "Solo esta"), "pm_pause": ("Pause", "Pausar"), "pm_resume": ("Resume", "Reanudar"), "pm_remove": ("Remove", "Quitar"),
 "pm_all": ("Activate all", "Activar todo"), "pm_clear": ("Clear position", "Vaciar posición"),
 "pm_hint_single": ("One strategy in the position. Switch to Combine to stack another one on top.", "Hay una sola estrategia en la posición. Cambia a Combinar para apilar otra encima."),
 "pm_hint_multi": ("Each block is a strategy you loaded. All active legs are valued together; use Only this to look at one in isolation.",
                   "Cada bloque es una estrategia que cargaste. Todas las patas activas se valoran en conjunto; usa Solo esta para verla aislada."),
 "vm_title": ("Your edits vs the market curve", "Tus cambios vs la curva de mercado"),
 "vm_d": ("Δ {x} (edited − market)", "Δ {x} (editada − mercado)"),
 "vm_line": ("Market curve (before your edits)", "Curva de mercado (antes de tus cambios)"),
 "vm_edited": ("edited: {q}", "editada: {q}"),
 "vm_max": ("Largest Δ zero", "Mayor Δ en la curva zero"),
 "vm_at": ("at {t}", "en {t}"),
 "vm_far": ("no effect here", "sin efecto aquí"),
 "vm_flat": ("The edit is real but too small to move the zero curve (below 0.005 bp). Edits to short deposits barely affect longer maturities.", "El cambio es real pero demasiado pequeño para mover la curva zero (menos de 0.005 bp). Editar depósitos cortos casi no afecta los plazos largos."),
 "pk_center": ("Center strike", "Strike central"),
 "pk_center_help": ("Presets build their strikes around this value (default: spot). Type your own and press Apply; it is kept when you switch preset.", "Los presets construyen sus strikes alrededor de este valor (por defecto: spot). Escribe el tuyo y pulsa Aplicar; se conserva al cambiar de preset."),
 "pk_width": ("Width (%)", "Ancho (%)"),
 "pk_width_help": ("Distance of the OTM strikes from the centre (wings of condors and ratios use 2×).", "Distancia de los strikes OTM al centro (las alas de condores y ratios usan 2×)."),
 "vm_none": ("No edits yet: change a quote or use the quick editor and the differences vs the market appear here.", "Sin cambios todavía: modifica una tasa o usa el editor rápido y aquí aparecerán las diferencias vs el mercado."),
}
