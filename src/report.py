"""Cifras del Informe ejecutivo (US-013, VS-016).

Las cifras salen de las mismas funciones que la pestaña "Cartera" con los parámetros base
(DEFAULT_PARAMS), de `models/metrics.json` y de `models/global_factors.json`, así que el
informe coincide con la aplicación. `python -m src.report` imprime las líneas en Markdown
para copiarlas a `reports/informe.md`.
"""
import json
from pathlib import Path

from src.config import MODELS_DIR
from src.finance import (
    DEFAULT_PARAMS,
    HIGH_RISK,
    SALIDA_PERMITIDA,
    SIN_ACCION,
    portfolio_kpis,
    realized_roi,
    score_portfolio,
    segment_matrix,
)
from src.inference import load_portfolio

# Nombres en español de las variables originales (los mismos que usa la app).
FEATURE_LABELS = {
    "CreditScore": "Puntaje crediticio", "Geography": "País", "Gender": "Género",
    "Age": "Edad", "Tenure": "Antigüedad", "Balance": "Saldo", "NumOfProducts": "Productos",
    "HasCrCard": "Tiene tarjeta", "IsActiveMember": "Miembro activo",
    "EstimatedSalary": "Salario estimado", "Satisfaction Score": "Satisfacción",
    "Card Type": "Tipo de tarjeta", "Point Earned": "Puntos",
}

VIP = DEFAULT_PARAMS.incentives[0].name
FEE_WAIVER = DEFAULT_PARAMS.incentives[1].name


def _money(x: float) -> str:
    """"$1,234.56" o "-$10.00" (SRS/BR-09), igual que la app."""
    return f"${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}"


def _pct(x: float | None) -> str:
    return "N/A" if x is None else f"{x * 100:,.1f}%"


def vip_threshold(params=DEFAULT_PARAMS) -> float:
    """Valor de Probabilidad de fuga × Margen a partir del cual Gestor VIP supera a la
    Exoneración de comisiones (US-013/BR-06 b): p·M·e_vip − c_vip > p·M·e_ex − c_ex."""
    vip, fee = params.incentives[0], params.incentives[1]
    return (vip.cost - fee.cost) / (vip.effectiveness - fee.effectiveness)


def report_numbers(models_dir=MODELS_DIR) -> dict:
    models_dir = Path(models_dir)
    portfolio = load_portfolio(models_dir / "portfolio_scored.csv")
    scored = score_portfolio(portfolio, DEFAULT_PARAMS)
    kpis = portfolio_kpis(scored)
    matrix = segment_matrix(scored, DEFAULT_PARAMS)

    with open(models_dir / "metrics.json", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(models_dir / "global_factors.json", encoding="utf-8") as f:
        factors = json.load(f)

    intervened = scored[~scored["decision"].isin([SALIDA_PERMITIDA, SIN_ACCION])]
    seg_d = scored[scored["segment"] == "D"]
    seg_d_int = intervened[intervened["segment"] == "D"]
    vip = scored[scored["decision"] == VIP]
    positive = scored.loc[scored["margin"] > 0, "margin"]
    medio = scored[scored["value_level"] == "Medio"]

    return {
        "n_customers": kpis.n_customers,
        "capital_at_risk": kpis.capital_at_risk,
        "capital_at_risk_critical": kpis.capital_at_risk_critical,
        "n_critical": int((scored["p_churn"] >= HIGH_RISK).sum()),
        "rescuable_capital": kpis.rescuable_capital,
        "investment": kpis.investment,
        "saved_margin": kpis.saved_margin,
        "roi": kpis.roi,
        "realized_roi_test": realized_roi(scored),
        "n_test_intervened": int((intervened["split"] == "test").sum()),
        "expected_avoided_churn": kpis.expected_avoided_churn,
        "avoided_churn_pct": kpis.avoided_churn_pct,
        "decision_counts": kpis.decision_counts,
        "segment_matrix": matrix,
        "roc_auc": float(metrics["roc_auc"]),
        "pr_auc": float(metrics["pr_auc"]),
        "brier_raw": float(metrics["brier_raw"]),
        "brier_calibrated": float(metrics["brier_calibrated"]),
        "n_test": int(metrics["n_test"]),
        "top_factors": [f["feature"] for f in factors[:3]],
        "factors": factors,
        # Explicaciones de US-013/BR-06.
        "seg_d_customers": len(seg_d),
        "seg_d_intervened": len(seg_d_int),
        "seg_d_investment": float(seg_d_int["incentive_cost"].sum()),
        "seg_d_gain": float(seg_d_int["expected_gain"].sum()),
        "seg_d_intervened_min_margin": float(seg_d_int["margin"].min()) if len(seg_d_int) else 0.0,
        "vip_threshold": vip_threshold(),
        "vip_customers": len(vip),
        "vip_min_p": float(vip["p_churn"].min()) if len(vip) else 0.0,
        "vip_min_margin": float(vip["margin"].min()) if len(vip) else 0.0,
        "seg_c_customers": int(matrix.loc["C", "Clientes"]),
        "n_deficit": int((scored["margin"] <= 0).sum()),
        "median_positive_margin": float(positive.median()),
        "medio_customers": len(medio),
        "medio_zero_balance": int((medio["Balance"] == 0).sum()),
    }


def _matrix_markdown(matrix) -> str:
    cols = list(matrix.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in matrix.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if c in ("Inversión en retención", "Ganancia neta esperada"):
                cells.append(_money(float(v)))
            elif isinstance(v, str):
                cells.append(v)
            else:
                cells.append(f"{int(v):,}")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def report_numbers_markdown(numbers: dict) -> str:
    n = numbers
    top = ", ".join(f"{FEATURE_LABELS.get(f, f)} (`{f}`)" for f in n["top_factors"])
    decisions = "\n".join(f"- {k}: {v:,}" for k, v in n["decision_counts"].items())
    return f"""## Sección 1: líneas de cifras
- Volumen Total de Clientes Analizados: {n["n_customers"]:,}
- Monto Total de Capital en Riesgo Crítico: {_money(n["capital_at_risk_critical"])}
- Capital Rescatable Estimado: {_money(n["rescuable_capital"])}
- Inversión Total en Campañas de Fidelización: {_money(n["investment"])}
- Retorno Sobre la Inversión (ROI): {_pct(n["roi"])} (proyectado; > 0 por construcción)
- ROI Realizado con la Efectividad Supuesta (Clientes de Prueba): {_pct(n["realized_roi_test"])}

## Sección 1: cifras de apoyo
- Capital en riesgo (Σ Saldo × Probabilidad de fuga): {_money(n["capital_at_risk"])}
- Clientes en riesgo crítico (Probabilidad de fuga ≥ 0.65): {n["n_critical"]:,}
- Margen salvado: {_money(n["saved_margin"])}
- Fugas evitadas esperadas: {n["expected_avoided_churn"]:,.2f} ({_pct(n["avoided_churn_pct"])})
- Clientes de prueba con Incentivo: {n["n_test_intervened"]:,}

## Sección 2: métricas y factores
Métricas de Diagnóstico Técnico: ROC-AUC: {n["roc_auc"]:.2f} | Precision-Recall AUC: {n["pr_auc"]:.2f} | Precisión de Calibración (Brier): {n["brier_calibrated"]:.3f}
- Brier sin calibrar: {n["brier_raw"]:.3f}; clientes de prueba: {n["n_test"]:,}
- Tres primeros Factores de fuga: {top}

## Sección 3: decisiones
{decisions}

## Sección 3: matriz por segmento
{_matrix_markdown(n["segment_matrix"])}

## Sección 3: explicaciones (US-013/BR-06)
- Segmento D: {n["seg_d_customers"]:,} clientes; {n["seg_d_intervened"]:,} con Incentivo; inversión {_money(n["seg_d_investment"])}; ganancia neta esperada {_money(n["seg_d_gain"])}; margen mínimo de los intervenidos {_money(n["seg_d_intervened_min_margin"])}
- Gestor VIP: umbral Probabilidad de fuga × Margen > {_money(n["vip_threshold"])}; {n["vip_customers"]:,} clientes; Probabilidad de fuga mínima {n["vip_min_p"]:.2f}; margen mínimo {_money(n["vip_min_margin"])}
- Segmento C: {n["seg_c_customers"]:,} clientes; clientes con Margen ≤ 0 en toda la Cartera: {n["n_deficit"]:,}
- Mediana del Margen positivo: {_money(n["median_positive_margin"])}; nivel Medio: {n["medio_customers"]:,} clientes, {n["medio_zero_balance"]:,} con saldo 0
"""


if __name__ == "__main__":
    print(report_numbers_markdown(report_numbers()))
