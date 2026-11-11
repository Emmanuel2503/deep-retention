---
id: VS-010
title: Ver los indicadores de la cartera
status: done
story: US-008
covers: [AC-01, AC-02, AC-03]
adrs: [ADR-0002, ADR-0007]
depends_on: [VS-002, VS-005]
---

# VS-010: Ver los indicadores de la cartera

## Goal
La Dirección de Estrategia abre la pestaña "Cartera" y ve el Volumen de clientes analizados, el Capital en riesgo, el Capital en riesgo crítico, el Capital rescatable, la Inversión en retención, el Margen salvado, el ROI, las Fugas evitadas esperadas y el número de clientes por Decisión de retención.

## Approach
Depende de VS-002 porque AC-03 se verifica con la Cartera puntuada real (`models/portfolio_scored.csv`); lo heredan VS-011, VS-012 y los slices del Simulador. `src/finance.py` agrega `portfolio_kpis(scored)`, que aplica SRS/BR-06 y EP-003/BR-03 a la Cartera ya puntuada por `score_portfolio`. La pestaña "Cartera" muestra cada indicador con `st.metric`, el conteo por Decisión con `st.dataframe` y la nota metodológica de EP-003/BR-01 con `st.caption`. Si la inversión es 0, el ROI se muestra "N/A".

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `PortfolioKpis`, `portfolio_kpis` | `src/finance.py` |
| UI | Pestaña "Cartera": métricas, conteo por decisión y nota | `app/app.py` |
| Data | Carteras puntuadas de ejemplo | `data/fixtures/portfolio_kpis.csv`, `data/fixtures/portfolio_no_gain.csv` |

## Contracts
```
# src/finance.py
PortfolioKpis = dataclass{
  n_customers: int, capital_at_risk: float, capital_at_risk_critical: float,
  rescuable_capital: float, investment: float, saved_margin: float,
  roi: float | None,                                                   # None si investment == 0
  expected_avoided_churn: float, avoided_churn_pct: float | None,      # None si no hay intervenidos
  decision_counts: dict[str, int]}
portfolio_kpis(scored: DataFrame) -> PortfolioKpis
  # capital_at_risk_critical = Σ Balance con p_churn >= HIGH_RISK

# app/app.py, pestaña "Cartera"
st.metric labels: "Clientes analizados" ("10,000"), "Capital en riesgo", "Capital en riesgo crítico",
  "Capital rescatable", "Inversión en retención", "Margen salvado", "ROI" ("231.2%" | "N/A"),
  "Fugas evitadas esperadas" ("0.24 (30.0%)")
st.dataframe columnas ["Decisión de retención", "Clientes"]
st.caption: "El 85% de estos clientes se usó para entrenar o calibrar la red."

# data/fixtures/portfolio_kpis.csv   → clientes 1001 y 1002 de portfolio_cases.csv
# data/fixtures/portfolio_no_gain.csv → solo el cliente 1002
```

## Tasks
- [x] **T-01:** Implementar `portfolio_kpis` → AC-01, AC-02
- [x] **T-02:** Mostrar métricas, conteo y nota en la pestaña "Cartera" → AC-01, AC-03
- [x] **T-03:** Mostrar "N/A" cuando la inversión es 0 → AC-02
- [x] **T-04:** Crear las Carteras de ejemplo → none

## Tests
Cada fila con `DEEP_RETENTION_PORTFOLIO=data/fixtures/<archivo>` salvo donde se indica la Cartera real (ADR-0006).

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Con `portfolio_kpis.csv`: Clientes 2, Capital en riesgo $80,000.00, Capital en riesgo crítico $100,000.00, Capital rescatable $24,000.00, Inversión $150.00, Margen salvado $496.80, ROI 231.2%, Fugas evitadas 0.24 (30.0%), 1 Exoneración de comisiones y 1 Salida Permitida | manual | app, pestaña "Cartera" |
| AC-02 | Con `portfolio_no_gain.csv`: Inversión $0.00 y ROI "N/A", sin trazas de error | manual | app, pestaña "Cartera" |
| AC-03 | Con la Cartera real (sin variable de entorno): Clientes analizados 10,000 y la nota del 85% visible | manual | app, pestaña "Cartera" |

## Out of scope
- Matriz de segmentos → VS-011.
- Filtro de Clientes de prueba y ROI realizado → VS-012.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
