"""Reglas financieras puras: margen, ganancias, decisiones e indicadores de la Cartera."""
from dataclasses import dataclass

import pandas as pd

# PROVISIONAL (VS-010): constantes del contrato de VS-005. Borrar este bloque al
# integrar VS-005 desde main, que define las mismas constantes.
SALIDA_PERMITIDA = "Salida Permitida"
SIN_ACCION = "Sin Acción Requerida"
HIGH_RISK = 0.65


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


def segment_matrix(scored: pd.DataFrame, params) -> pd.DataFrame:
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
