---
id: EP-002
title: Consultar la decisión de retención de un cliente
status: ready
priority: high
requirements: [FR-03]
---

# EP-002: Consultar la decisión de retención de un cliente

## Goal
El Ejecutivo de cuentas consulta a un cliente, existente o nuevo, en el Buscador por cliente y ve su Probabilidad de fuga, el impacto monetario de cada Incentivo y la Decisión de retención sugerida, con su justificación. Así aplica la retención solo cuando es rentable, sin conocimientos técnicos.

## Actors
- Ejecutivo de cuentas (main actor).

## Shared business rules
- **BR-01:** Toda consulta muestra, como mínimo: Probabilidad de fuga, Margen del cliente, Ganancia neta esperada de cada Incentivo, Decisión de retención y Segmento.

## Done when
- [ ] **DW-01:** Un Ejecutivo de cuentas obtiene la Decisión de retención de cualquier cliente del dataset a partir de su identificador.
- [ ] **DW-02:** Un Ejecutivo de cuentas obtiene la Decisión de retención de un cliente que no está en el dataset ingresando sus datos, sin errores no controlados.
- [ ] **DW-03:** Cada consulta muestra qué variables del cliente aumentaron o redujeron su Probabilidad de fuga.

## Out of scope
- Registrar que el Incentivo se aplicó al cliente.
- Consultar varios clientes a la vez (lo cubre EP-003).

## Open questions
- [x] **Q-01:** ¿Con cuántos decimales se muestran los montos y la Probabilidad de fuga? → **A:** Dos en ambos casos (SRS/BR-09).
