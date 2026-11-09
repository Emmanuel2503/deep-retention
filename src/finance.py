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


def portfolio_kpis(scored: pd.DataFrame) -> PortfolioKpis:
    """Indicadores de SRS/BR-06 y EP-003/BR-03 sobre una Cartera ya puntuada por `score_portfolio`."""
    p = scored["p_churn"]
    intervened = scored[~scored["decision"].isin([SALIDA_PERMITIDA, SIN_ACCION])]
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
