---
id: VS-013
title: Ajustar costo y efectividad de los incentivos
status: done
story: US-011
covers: [AC-01, AC-02]
adrs: [ADR-0007]
depends_on: [VS-010]
---

# VS-013: Ajustar costo y efectividad de los incentivos

## Goal
En la pestaña "Simulador", la Dirección de Estrategia cambia el costo o la Efectividad de un Incentivo y ve el cambio en las Decisiones de retención del Buscador y en los indicadores de la Cartera en la misma interacción; los valores inválidos se rechazan con el rango permitido.

## Approach
La pestaña "Simulador" muestra, por cada Incentivo, un `number_input` de costo ($) y otro de Efectividad (%), sin `min_value`, `max_value` ni `value`: al inicio del script, las claves de los widgets se inicializan en `st.session_state` con `widget_defaults(params)` si no existen. Cada `number_input` tiene `on_change=on_incentive_change`, un callback que lee los dos valores del Incentivo de `st.session_state`, los valida con `validate_incentive` y, si son válidos, reemplaza `st.session_state["params"]` con `with_incentive`; si no, guarda el mensaje en `st.session_state["sim_errors"]` y conserva los parámetros anteriores. Streamlit ejecuta los callbacks antes del script, así que el Buscador y la Cartera, que se dibujan antes que el Simulador, ya usan los parámetros nuevos (ADR-0007). La pestaña "Simulador" muestra un `st.error` por cada mensaje de `sim_errors`.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `validate_incentive` | `src/validation.py` |
| Domain | `with_incentive`, `widget_defaults` | `src/finance.py` |
| UI | Entradas de Incentivos en "Simulador", inicialización de claves y callback | `app/app.py` |

## Contracts
```
# src/validation.py
validate_incentive(cost: float, effectiveness_pct: float) -> str | None
  # "El costo debe ser ≥ 0" | "La efectividad debe estar entre 0% y 100%" | None

# src/finance.py
with_incentive(params, index: int, cost: float, effectiveness: float) -> Params   # effectiveness en 0..1
widget_defaults(params) -> dict[str, float]
  # {"cost_0": 500, "eff_0": 40, "cost_1": 150, "eff_1": 30, "cost_2": 50, "eff_2": 20}  (con DEFAULT_PARAMS)
  # VS-014 agrega las claves del margen

# app/app.py, pestaña "Simulador"
for k, v in widget_defaults(params).items(): st.session_state.setdefault(k, v)   # al inicio del script
number_input key="cost_<i>" ($), key="eff_<i>" (%), i = 0 VIP, 1 Exoneración, 2 Bonificación,
             on_change=on_incentive_change, args=(i,)
st.session_state["sim_errors"]: dict[str, str]    # "incentive_<i>" → mensaje
st.error(mensaje) por cada entrada de sim_errors; params sin cambios
```

## Tasks
- [x] **T-01:** Implementar `validate_incentive`, `with_incentive` y `widget_defaults` → AC-01, AC-02
- [x] **T-02:** Crear las entradas en "Simulador", inicializar sus claves y actualizar `params` en el callback → AC-01
- [x] **T-03:** Guardar y mostrar el error y conservar los parámetros si el valor es inválido → AC-02

## Tests
Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv` (ADR-0006).

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Poner `cost_1` = 400 y pulsar Enter; sin ninguna otra interacción, la pestaña "Cartera" ya muestra Inversión $50.00 y ROI 562.4%, y buscar 1001 muestra Decisión "Bonificación transaccional" con ganancias 281.20 y 96.80 | manual | app, pestañas "Simulador", "Cartera" y "Buscador" |
| AC-02 | Poner `eff_0` = 120 muestra un error con "0% y 100%", y la Inversión y el ROI de "Cartera" quedan iguales a los iniciales | manual | app, pestañas "Simulador" y "Cartera" |

## Out of scope
- Parámetros del Margen del cliente → VS-014.
- Restablecer valores base y alcance por sesión (AC-03, AC-04) → VS-015.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
