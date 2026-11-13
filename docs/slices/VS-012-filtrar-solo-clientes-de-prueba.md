---
id: VS-012
title: Filtrar solo clientes de prueba
status: done
story: US-010
covers: [AC-01, AC-02, AC-03]
adrs: [ADR-0002, ADR-0007]
depends_on: [VS-011]
---

# VS-012: Filtrar solo clientes de prueba

## Goal
En la pestaña "Cartera", la Dirección de Estrategia activa "Solo clientes de prueba" y ve los indicadores y la matriz calculados solo con los 1,500 Clientes de prueba, más el ROI realizado; al desactivarlo vuelve a la Cartera completa.

## Approach
La pestaña "Cartera" agrega un `st.toggle`. La Cartera completa se puntúa siempre con `score_portfolio` (la mediana de niveles de valor sale de los 10,000 clientes) y, si el toggle está activo, la Cartera ya puntuada se filtra por `split == "test"` antes de llamar a `portfolio_kpis` y `segment_matrix`. Con el toggle activo se muestra además `realized_roi` (SRS/BR-06, SRS/OBJ-03), que usa `Exited` en lugar de `p_churn`. La nota del 85% solo se muestra con la Cartera completa. VS-016 reutiliza `realized_roi` para el Informe ejecutivo.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `realized_roi` | `src/finance.py` |
| UI | Toggle "Solo clientes de prueba", filtro y métrica "ROI realizado" | `app/app.py` |

## Contracts
```
# src/finance.py
realized_roi(scored: DataFrame) -> float | None
  # filas con split == "test" e Incentivo asignado:
  # (Σ Exited × incentive_effectiveness × margin − Σ incentive_cost) / Σ incentive_cost
  # None si ninguna fila tiene Incentivo

# app/app.py, pestaña "Cartera"
st.toggle("Solo clientes de prueba", key="only_test", value=False)
st.metric "ROI realizado" ("314.0%" | "N/A"), solo con only_test activo
```

## Tasks
- [x] **T-01:** Agregar el toggle y filtrar antes de calcular indicadores y matriz → AC-01, AC-02
- [x] **T-02:** Implementar `realized_roi` y mostrarlo con el toggle activo → AC-03

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Con la Cartera real, activar "Solo clientes de prueba" muestra Clientes analizados 1,500 y la suma de "Clientes" de la matriz es 1,500 | manual | app, pestaña "Cartera" |
| AC-02 | Desactivarlo vuelve a mostrar 10,000 y los mismos valores de las métricas que antes de activarlo, sin "ROI realizado" | manual | app, pestaña "Cartera" |
| AC-03 | Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv`, activar el toggle muestra ROI realizado 314.0%; con `portfolio_no_gain.csv`, "N/A" | manual | app, pestaña "Cartera" |

## Out of scope
- Filtros por otras variables.

## Open questions
- [x] **Q-01:** Con el filtro activo, ¿la mediana que separa los niveles de valor Medio y Superior (SRS/BR-05) se calcula solo con los Clientes de prueba o se mantiene la de la Cartera completa? Cambia los Segmentos A y B, aunque no las Decisiones de retención. → **A:** Se mantiene la de la Cartera completa: primero se puntúa y después se filtra, así cada cliente conserva su Segmento.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
