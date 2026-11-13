---
id: VS-007
title: Evaluar un cliente nuevo por formulario
status: done
story: US-006
covers: [AC-01, AC-03]
adrs: [ADR-0002, ADR-0007]
depends_on: [VS-002, VS-005]
---

# VS-007: Evaluar un cliente nuevo por formulario

## Goal
El Ejecutivo de cuentas elige "Cliente nuevo" en el Buscador, completa el formulario con las variables de entrada y ve la Probabilidad de fuga, el Margen del cliente, las Ganancias netas esperadas, el Segmento y la Decisión de retención.

## Approach
Con `search_mode = "Cliente nuevo"`, la pestaña "Buscador" muestra un `st.form` con un campo por cada variable de `ChurnPredictor.features` (VS-002). Las variables categóricas son `selectbox` con las opciones de `features.json["categories"]`; `HasCrCard` e `IsActiveMember` son `checkbox` (marcado = 1), así que no admiten otros valores (US-006/BR-01); el resto son `number_input`. Al enviar, la app arma un DataFrame de una fila, obtiene la Probabilidad de fuga con `ChurnPredictor.predict` (cargado con `st.cache_resource`) y la pasa por las mismas funciones de `src/finance.py`. El nivel de valor usa la mediana de la Cartera puntuada con los parámetros vigentes (`value_level_for(margin, median)`). Los resultados se muestran con los mismos elementos que VS-005.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `median_positive_margin`, `value_level_for`, `evaluate_customer` | `src/finance.py` |
| UI | Formulario de cliente nuevo y resultados | `app/app.py` |

## Contracts
```
# src/finance.py
median_positive_margin(scored: DataFrame) -> float
value_level_for(margin: float, median: float) -> str
CustomerResult = dataclass{p_churn: float, margin: float, segment: str, decision: Decision}
evaluate_customer(p_churn: float, balance: float, num_products: int, has_card: int,
                  median: float, params) -> CustomerResult
  # la búsqueda por identificador de VS-005 se refactoriza para usar evaluate_customer

# app/app.py
st.form key="new_customer"; campos key="f_<columna>" (p. ej. "f_Balance", "f_Geography")
selectbox para Geography, Gender, Card Type con predictor.categories[col]
checkbox para HasCrCard e IsActiveMember (True → 1, False → 0)
form_submit_button "Evaluar"
resultados: mismos st.metric y st.dataframe que VS-005
```

## Tasks
- [ ] **T-01:** Implementar `median_positive_margin`, `value_level_for` y `evaluate_customer`, y usarlos en la búsqueda por identificador → AC-01
- [ ] **T-02:** Crear el formulario con selectbox para las categóricas y checkbox para las binarias → AC-03
- [ ] **T-03:** Predecir con `ChurnPredictor` y mostrar los resultados → AC-01

## Tests
Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv` y el modelo real de `models/`.

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Enviar Balance 250,000, 2 productos, con tarjeta y el resto válido muestra Margen $5,070.00, una Probabilidad de fuga en [0, 1] y la Decisión que corresponde a esa probabilidad según SRS/BR-01 y BR-02 (recalcular a mano las tres ganancias) | manual | app, pestaña "Buscador", modo "Cliente nuevo" |
| AC-03 | El selectbox `f_Geography` ofrece exactamente France, Germany y Spain; `f_HasCrCard` y `f_IsActiveMember` son casillas Sí/No | manual | app, pestaña "Buscador", modo "Cliente nuevo" |

## Out of scope
- Validación de límites de negocio (AC-02, AC-04) → VS-008.
- Explicación del cliente → VS-009.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Ainhoa (turno 2)
