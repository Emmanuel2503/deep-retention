---
id: VS-008
title: Validar los límites de negocio del formulario
status: ready
story: US-006
covers: [AC-02, AC-04]
adrs: []
depends_on: [VS-007]
---

# VS-008: Validar los límites de negocio del formulario

## Goal
Si el Ejecutivo de cuentas ingresa un valor fuera de los límites de negocio o deja un campo vacío, ve junto al campo el rango permitido y ningún resultado; los valores dentro de los límites se aceptan aunque no aparezcan en el dataset.

## Approach
`src/validation.py` define los límites de US-006/BR-02 y `validate_customer`, que devuelve un mensaje por cada campo inválido o vacío. Los `number_input` del formulario no tienen `min_value` ni `max_value`, para que la validación sea siempre la de `src/`. `HasCrCard` e `IsActiveMember` no se validan aquí porque son casillas (VS-007). Si hay errores, la app muestra un `st.error` por campo y no predice.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `Limit`, `BUSINESS_LIMITS`, `validate_customer` | `src/validation.py` |
| UI | Mensajes por campo y bloqueo de resultados | `app/app.py` |

## Contracts
```
# src/validation.py
Limit = dataclass{min: float | None, max: float | None, integer: bool}
BUSINESS_LIMITS = {
  "CreditScore": Limit(300, 850, True), "Age": Limit(18, 100, True), "Tenure": Limit(0, 50, True),
  "Balance": Limit(0, None, False), "NumOfProducts": Limit(1, None, True),
  "EstimatedSalary": Limit(0, None, False), "Satisfaction Score": Limit(1, 5, True),
  "Point Earned": Limit(0, None, True),
}
validate_customer(values: dict[str, object]) -> dict[str, str]   # campo → mensaje; {} si es válido
  # mensaje: "<Campo>: debe estar entre 18 y 100" | "<Campo>: debe ser ≥ 0" |
  #          "<Campo>: debe ser un entero" | "<Campo>: es obligatorio" (valor None)

# app/app.py
un st.error(mensaje) por campo inválido; ningún st.metric de resultados
```

## Tasks
- [ ] **T-01:** Implementar `Limit`, `BUSINESS_LIMITS` y `validate_customer` → AC-02, AC-04
- [ ] **T-02:** Quitar límites de los `number_input`, mostrar los errores y bloquear la predicción → AC-02

## Tests
Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv` y el modelo real de `models/`.

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-02 | Enviar Balance -100 muestra un error que nombra Balance y "≥ 0", sin métricas de resultado ni trazas de error; dejar Age vacío muestra "Age: es obligatorio" | manual | app, pestaña "Buscador", modo "Cliente nuevo" |
| AC-04 | Enviar NumOfProducts 6 muestra resultados; enviar Age 17 muestra un error con "entre 18 y 100" y ningún resultado | manual | app, pestaña "Buscador", modo "Cliente nuevo" |

## Out of scope
- Validación de los parámetros del Simulador → VS-013, VS-014.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Ainhoa (turno 2)
