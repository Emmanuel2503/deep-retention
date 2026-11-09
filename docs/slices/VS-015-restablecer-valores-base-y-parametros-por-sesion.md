---
id: VS-015
title: Restablecer valores base y parámetros por sesión
status: ready
story: US-011
covers: [AC-03, AC-04]
adrs: [ADR-0007]
depends_on: [VS-013, VS-014]
---

# VS-015: Restablecer valores base y parámetros por sesión

## Goal
La Dirección de Estrategia pulsa "Restablecer valores base" y todos los parámetros del Simulador, de Incentivos y de margen, vuelven a los valores base; una sesión nueva siempre empieza con los valores base.

## Approach
Un `st.button` con callback `reset_params` asigna `DEFAULT_PARAMS` a `st.session_state["params"]`, repone las claves de los `number_input` con `widget_defaults(DEFAULT_PARAMS)` (VS-013, VS-014) para que la interfaz y los parámetros coincidan, y vacía `sim_errors`. Los parámetros no se guardan fuera de la sesión (ADR-0007/F-03), así que una sesión nueva parte de `DEFAULT_PARAMS`.

## Changes
| Layer | Change | Location |
|---|---|---|
| UI | Botón "Restablecer valores base" y callback | `app/app.py` |

## Contracts
```
# app/app.py, pestaña "Simulador"
st.button("Restablecer valores base", key="reset_params", on_click=reset_params)
reset_params(): params = DEFAULT_PARAMS; claves de widget_defaults(DEFAULT_PARAMS); sim_errors = {}
```

## Tasks
- [ ] **T-01:** Implementar el botón y el callback de restablecimiento → AC-03
- [ ] **T-02:** Comprobar que ningún parámetro se guarda fuera de `st.session_state` → AC-04

## Tests
Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv` (ADR-0006).

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-03 | Poner `cost_1` = 400 y `spread` = 0, pulsar "Restablecer valores base": `cost_1` vale 150, `spread` vale 2 y las métricas de "Cartera" son iguales a las iniciales | manual | app, pestañas "Simulador" y "Cartera" |
| AC-04 | Tras cambiar `cost_1`, abrir la app en otra pestaña del navegador (sesión nueva): `cost_1` vale 150 y los indicadores son los iniciales | manual | app, dos pestañas del navegador |

## Out of scope
- Guardar escenarios.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
