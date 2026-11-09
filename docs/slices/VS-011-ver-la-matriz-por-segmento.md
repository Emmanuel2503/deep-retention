---
id: VS-011
title: Ver la matriz por segmento
status: ready
story: US-009
covers: [AC-01, AC-02, AC-03]
adrs: [ADR-0007]
depends_on: [VS-010]
---

# VS-011: Ver la matriz por segmento

## Goal
En la pestaña "Cartera", la Dirección de Estrategia ve una fila por Segmento (A a E) con el número de clientes, el rango de Probabilidad de fuga, el nivel de valor, los clientes por Decisión de retención, la Inversión en retención y la Ganancia neta esperada total.

## Approach
`src/finance.py` agrega `segment_matrix(scored, params)`, que agrupa la Cartera puntuada por Segmento y siempre devuelve las cinco filas, incluidas las vacías con ceros; usa `params.incentives` solo para nombrar las columnas de Decisión. La pestaña "Cartera" la muestra con `st.dataframe` debajo de los indicadores.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `segment_matrix` | `src/finance.py` |
| UI | Matriz en la pestaña "Cartera" | `app/app.py` |

## Contracts
```
# src/finance.py
SEGMENT_INFO = {
  "A": ("Alto valor / Alto riesgo", "≥ 0.65", "Superior"),
  "B": ("Medio / Riesgo moderado", "≥ 0.65", "Medio"),
  "C": ("No rentable", "≥ 0.65", "Bajo/Deficitario"),
  "D": ("Estable", "< 0.30", "Cualquiera"),
  "E": ("Riesgo intermedio", "0.30 – 0.65", "Cualquiera")}
segment_matrix(scored: DataFrame, params) -> DataFrame
  # índice A..E (siempre 5 filas); columnas:
  # "Segmento", "Probabilidad de fuga", "Nivel de valor", "Clientes",
  # una columna por cada Decisión posible (nombres de Incentivos, SALIDA_PERMITIDA, SIN_ACCION),
  # "Inversión en retención", "Ganancia neta esperada"
```

## Tasks
- [ ] **T-01:** Implementar `segment_matrix` con las cinco filas siempre presentes → AC-01, AC-02, AC-03
- [ ] **T-02:** Mostrar la matriz en la pestaña "Cartera" → AC-01

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Con la Cartera real: la suma de "Clientes" de A a E es 10,000 y la suma de "Inversión en retención" es igual a la métrica "Inversión en retención" | manual | app, pestaña "Cartera" |
| AC-02 | Con `portfolio_cases.csv`: el Segmento C tiene 1 cliente (1004) y el E tiene 2 (1002 y 1005) | manual | app, pestaña "Cartera" |
| AC-03 | Con `portfolio_no_gain.csv`: las filas A, B y C tienen 0 clientes y $0.00 | manual | app, pestaña "Cartera" |

## Out of scope
- Detalle de clientes por Segmento.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
