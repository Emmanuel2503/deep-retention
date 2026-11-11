---
id: VS-006
title: Rechazar identificadores inválidos
status: done
story: US-005
covers: [AC-03]
adrs: []
depends_on: [VS-005]
---

# VS-006: Rechazar identificadores inválidos

## Goal
Si el Ejecutivo de cuentas busca un identificador que no existe, un texto no numérico o un campo vacío, ve un mensaje claro y ningún resultado, sin que la aplicación falle.

## Approach
`src/validation.py` agrega `parse_customer_id`, que convierte el texto o devuelve el mensaje de error. La pestaña "Buscador" muestra `st.error` con ese mensaje si el identificador no es válido, o `st.warning("Cliente no encontrado")` si es válido pero no está en la Cartera, y en ambos casos no dibuja resultados.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `parse_customer_id` | `src/validation.py` |
| UI | Mensajes de error y de cliente no encontrado en "Buscador" | `app/app.py` |

## Contracts
```
# src/validation.py
ID_ERROR = "El identificador debe ser numérico."
NOT_FOUND = "Cliente no encontrado"
parse_customer_id(text: str) -> tuple[int | None, str | None]   # (id, None) o (None, ID_ERROR)

# app/app.py
st.error(ID_ERROR)     si parse_customer_id devuelve error
st.warning(NOT_FOUND)  si el id no está en la Cartera
ningún st.metric de resultados en ambos casos
```

## Tasks
- [x] **T-01:** Implementar `parse_customer_id` → AC-03
- [x] **T-02:** Mostrar los mensajes en "Buscador" y omitir los resultados → AC-03

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-03 | Con `portfolio_cases.csv`, buscar "999999" muestra "Cliente no encontrado"; buscar "abc" y "" muestran "El identificador debe ser numérico."; en los tres casos no hay métricas de resultado ni trazas de error | manual | app, pestaña "Buscador" |

## Out of scope
- Validación del formulario de cliente nuevo → VS-008.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Ainhoa (turno 2)
