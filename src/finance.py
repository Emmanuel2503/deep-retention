"""
Módulo de Lógica Financiera y Reglas de Negocio (Deep Retention)
"""
from dataclasses import dataclass, replace
from typing import Dict, Optional, Union
import pandas as pd
import numpy as np

SALIDA_PERMITIDA = "Salida Permitida"
SIN_ACCION = "Sin Acción Requerida"
HIGH_RISK = 0.65
LOW_RISK = 0.30

@dataclass(frozen=True)
class Incentive:
    name: str
    cost: float
    effectiveness: float          # 0..1

@dataclass(frozen=True)
class Params:
    spread: float = 0.02
    fee_per_product: float = 50.0
    fee_card: float = 30.0
    service_cost: float = 60.0
    incentives: tuple[Incentive, ...] = (
        Incentive("Gestor VIP y tarifa plana", 500.0, 0.40),
        Incentive("Exoneración de comisiones", 150.0, 0.30),
        Incentive("Bonificación transaccional", 50.0, 0.20),
    )

DEFAULT_PARAMS = Params()

def customer_margin(
    balance: Union[float, pd.Series],
    num_products: Union[int, pd.Series],
    has_card: Union[int, pd.Series],
    params: Params
    ) -> Union[float, pd.Series]:
    margen = (
        (balance * params.spread)
        + (num_products * params.fee_per_product)
        + (has_card * params.fee_card)
        - params.service_cost
    )
    if isinstance(margen, pd.Series):
        return margen.round(2)
    return round(float(margen), 2)

def expected_net_gains(p: float, margin: float, params: Params) -> Dict[str, float]:
    gains = {}
    for inc in params.incentives:
        gne = (p * inc.effectiveness * margin) - inc.cost
        gains[inc.name] = round(float(gne), 2)
    return gains

def value_level_for(margin: float, median: float) -> str:
    if margin <= 0:
        return "Bajo/Deficitario"
    elif margin <= median:
        return "Medio"
    else:
        return "Superior"

def value_level(margins: pd.Series) -> pd.Series:
    pos_margins = margins[margins > 0]
    mediana = float(pos_margins.median()) if len(pos_margins) > 0 else 1000.0

    conditions = [
        margins <= 0,
        (margins > 0) & (margins <= mediana),
        margins > mediana
    ]
    choices = ["Bajo/Deficitario", "Medio", "Superior"]

    return pd.Series(np.select(conditions, choices, default="Bajo/Deficitario"), index=margins.index)

def segment(p: float, level: str) -> str:
    if p < LOW_RISK:
        return "D"
    elif p < HIGH_RISK:
        return "E"
    else:
        if level == "Bajo/Deficitario":
            return "C"
        elif level == "Medio":
            return "B"
        else: return "A"

@dataclass
class Decision:
    label: str
    incentive: Optional[Incentive]
    gains: Dict[str, float]

def decide(p: float, margin: float, seg_code: str, params: Params) -> Decision:
    gains = expected_net_gains(p, margin, params)

    best_inc: Optional[Incentive] = None
    max_gain = -float("inf")

    for inc in params.incentives:
        g = gains.get(inc.name, -float("inf"))
        if g > max_gain:
            max_gain = g
            best_inc = inc

    if max_gain > 0 and best_inc is not None:
        label = best_inc.name
        inc_obj = best_inc
    else:
        inc_obj = None
        label = SIN_ACCION if seg_code == "D" else SALIDA_PERMITIDA

    return Decision(label=label, incentive=inc_obj, gains=gains)

@dataclass
class CustomerResult:
    p_churn: float
    margin: float
    segment: str
    decision: Decision

def evaluate_customer(
    p_churn: float,
    balance: float,
    num_products: int,
    has_card: int,
    median: float,
    params: Params
) -> CustomerResult:
    margin = float(customer_margin(balance, num_products, has_card, params))
    v_level = value_level_for(margin, median)
    seg_code = segment(p_churn, v_level)
    decision = decide(p_churn, margin, seg_code, params)
    return CustomerResult(p_churn=p_churn, margin=margin, segment=seg_code, decision=decision)

def score_portfolio(portfolio: pd.DataFrame, params: Params) -> pd.DataFrame:
    df = portfolio.copy()
    df["margin"] = customer_margin(df["Balance"], df["NumOfProducts"], df["HasCrCard"], params)
    df["value_level"] = value_level(df["margin"])
    pos_margins = df[df["margin"] > 0]["margin"]
    mediana = float(pos_margins.median()) if len(pos_margins) > 0 else 1000.0
    decisions = []
    incentive_costs = []
    incentive_effs = []
    expected_gains = []
    gain_cols = {f"gain__{inc.name}": [] for inc in params.incentives}

    for _, row in df.iterrows():
        p_ch = float(row["p_churn"])
        m = float(row["margin"])
        v_lev = value_level_for(m, mediana)
        seg = segment(p_ch, v_lev)
        dec = decide(p_ch, m, seg, params)

        decisions.append(dec.label)

        if dec.incentive is not None:
            incentive_costs.append(float(dec.incentive.cost))
            incentive_effs.append(float(dec.incentive.effectiveness))
            expected_gains.append(float(dec.gains[dec.incentive.name]))
        else:
            incentive_costs.append(0.0)
            incentive_effs.append(0.0)
            expected_gains.append(0.0)

        for inc in params.incentives:
            gain_cols[f"gain__{inc.name}"].append(dec.gains[inc.name])

    df["segment"] = [segment(float(r["p_churn"]), value_level_for(float(r["margin"]), mediana)) for _, r in df.iterrows()]
    df["decision"] = decisions
    df["incentive_cost"] = incentive_costs
    df["incentive_effectiveness"] = incentive_effs
    df["expected_gain"] = expected_gains
    for col_name, values in gain_cols.items():
        df[col_name] = values

    return df


# --- Indicadores de la Cartera (VS-010) ---


@dataclass(frozen=True)
class PortfolioKpis:
    n_customers: int
    capital_at_risk: float
    capital_at_risk_critical: float
    rescuable_capital: float
    investment: float
    saved_margin: float
    roi: float | None  # None si investment == 0
    expected_avoided_churn: float
    avoided_churn_pct: float | None  # None si no hay intervenidos
    decision_counts: dict[str, int]


def _intervened(scored: pd.DataFrame) -> pd.DataFrame:
    """Clientes con Incentivo asignado: su decisión no es una de las decisiones sin gasto."""
    return scored[~scored["decision"].isin([SALIDA_PERMITIDA, SIN_ACCION])]


def portfolio_kpis(scored: pd.DataFrame) -> PortfolioKpis:
    """Indicadores de SRS/BR-06 y EP-003/BR-03 sobre una Cartera ya puntuada por `score_portfolio`."""
    p = scored["p_churn"]
    intervened = _intervened(scored)
    p_int = intervened["p_churn"]
    eff_int = intervened["incentive_effectiveness"]

    investment = float(intervened["incentive_cost"].sum())
    saved_margin = float((p_int * eff_int * intervened["margin"]).sum())
    expected_avoided = float((p_int * eff_int).sum())
    expected_churn = float(p_int.sum())

    return PortfolioKpis(
        n_customers=len(scored),
        capital_at_risk=float((scored["Balance"] * p).sum()),
        capital_at_risk_critical=float(scored.loc[p >= HIGH_RISK, "Balance"].sum()),
        rescuable_capital=float((intervened["Balance"] * p_int * eff_int).sum()),
        investment=investment,
        saved_margin=saved_margin,
        roi=(saved_margin - investment) / investment if investment > 0 else None,
        expected_avoided_churn=expected_avoided,
        avoided_churn_pct=expected_avoided / expected_churn if len(intervened) > 0 and expected_churn > 0 else None,
        decision_counts={str(k): int(v) for k, v in scored["decision"].value_counts().items()},
    )


# --- Matriz por Segmento (VS-011) ---

# Segmento → (nombre, rango de Probabilidad de fuga, nivel de valor), según SRS/BR-05.
SEGMENT_INFO = {
    "A": ("Alto valor / Alto riesgo", "≥ 0.65", "Superior"),
    "B": ("Medio / Riesgo moderado", "≥ 0.65", "Medio"),
    "C": ("No rentable", "≥ 0.65", "Bajo/Deficitario"),
    "D": ("Estable", "< 0.30", "Cualquiera"),
    "E": ("Riesgo intermedio", "0.30 – 0.65", "Cualquiera"),
}


def segment_matrix(scored: pd.DataFrame, params: Params) -> pd.DataFrame:
    """Una fila por Segmento A..E, incluidas las vacías con ceros.

    `params.incentives` solo se usa para nombrar las columnas de Decisión.
    """
    decisions = [inc.name for inc in params.incentives] + [SALIDA_PERMITIDA, SIN_ACCION]
    intervened = _intervened(scored)
    rows = []
    for seg, (name, p_range, level) in SEGMENT_INFO.items():
        in_seg = scored[scored["segment"] == seg]
        int_seg = intervened[intervened["segment"] == seg]
        counts = in_seg["decision"].value_counts()
        rows.append({
            "Segmento": name,
            "Probabilidad de fuga": p_range,
            "Nivel de valor": level,
            "Clientes": len(in_seg),
            **{d: int(counts.get(d, 0)) for d in decisions},
            "Inversión en retención": float(int_seg["incentive_cost"].sum()),
            "Ganancia neta esperada": float(int_seg["expected_gain"].sum()),
        })
    return pd.DataFrame(rows, index=list(SEGMENT_INFO))


# --- ROI realizado (VS-012) ---


def realized_roi(scored: pd.DataFrame) -> float | None:
    """ROI realizado de SRS/BR-06 sobre los Clientes de prueba con Incentivo asignado.

    Usa el abandono real (`Exited`) en lugar de la Probabilidad de fuga, así que puede
    ser negativo. None si ningún Cliente de prueba tiene Incentivo.
    """
    test = _intervened(scored[scored["split"] == "test"])
    investment = float(test["incentive_cost"].sum())
    if len(test) == 0 or investment == 0:
        return None
    realized = float((test["Exited"] * test["incentive_effectiveness"] * test["margin"]).sum())
    return (realized - investment) / investment


# --- Simulador: Incentivos (VS-013) ---


def with_incentive(params: Params, index: int, cost: float, effectiveness: float) -> Params:
    """Copia de `params` con el costo y la Efectividad (0..1) del Incentivo `index` cambiados."""
    incentives = list(params.incentives)
    incentives[index] = replace(incentives[index], cost=float(cost), effectiveness=float(effectiveness))
    return replace(params, incentives=tuple(incentives))


def widget_defaults(params: Params) -> dict[str, float]:
    """Valores de las entradas del Simulador para `params`; la Efectividad y el Spread, en porcentaje."""
    defaults = {}
    for i, inc in enumerate(params.incentives):
        defaults[f"cost_{i}"] = inc.cost
        # round: 0.4 * 100 da 40.00000000000001 en coma flotante.
        defaults[f"eff_{i}"] = round(inc.effectiveness * 100, 6)
    # Margen del cliente (VS-014).
    defaults["spread"] = round(params.spread * 100, 6)
    defaults["fee_per_product"] = params.fee_per_product
    defaults["fee_card"] = params.fee_card
    defaults["service_cost"] = params.service_cost
    return defaults
