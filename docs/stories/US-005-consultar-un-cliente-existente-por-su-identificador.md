---
id: US-005
title: Consultar un cliente existente por su identificador
status: done
priority: high
epic: EP-002
---

# US-005: Consultar un cliente existente por su identificador

## Story
**As a** Ejecutivo de cuentas
**I want** buscar a un cliente por su identificador y ver su Decisión de retención
**so that** sepa si debo ofrecerle un Incentivo y cuál.

## Context
El enunciado pide una entrada individual para ejecutivos donde se vea el puntaje de la red, el impacto monetario proyectado y la decisión comercial sugerida.

## Actors
- **Primary:** Ejecutivo de cuentas.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** El Ejecutivo de cuentas está en el Buscador por cliente.

## Basic flow
- **BF-01:** El Ejecutivo de cuentas ingresa el identificador del cliente (`CustomerId`).
- **BF-02:** System obtiene los datos del cliente y estima su Probabilidad de fuga.
- **BF-03:** System calcula el Margen del cliente y la Ganancia neta esperada de cada Incentivo.
- **BF-04:** System muestra la Probabilidad de fuga, el Margen del cliente, la Ganancia neta esperada de cada Incentivo, el Segmento y la Decisión de retención.

## Alternate flows
- **AF-01** (from BF-02): If el identificador no existe en la Cartera, then System muestra "Cliente no encontrado" y no muestra resultados. → End.
- **AF-02** (from BF-01): If el identificador está vacío o no es numérico, then System muestra un mensaje indicando que el identificador debe ser numérico. → End.

## Post-conditions
- **POST-01:** El Ejecutivo de cuentas ve la Decisión de retención del cliente.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-04): Given un cliente con Balance $100,000, 2 productos, con tarjeta y Probabilidad de fuga 0.80, con los parámetros base, when el Ejecutivo de cuentas busca su identificador, then ve Margen del cliente $2,070, Ganancia neta esperada de Gestor VIP $162.40, de Exoneración de comisiones $346.80 y de Bonificación transaccional $281.20, y la Decisión de retención "Exoneración de comisiones".
- **AC-02** (BF-01..BF-04): Given un cliente con Balance $0, 1 producto, sin tarjeta y Probabilidad de fuga 0.50, con los parámetros base, when el Ejecutivo de cuentas busca su identificador, then ve Margen del cliente −$10.00, todas las Ganancias netas esperadas negativas y la Decisión de retención "Salida Permitida".
- **AC-03** (AF-01..AF-02): Given un identificador que no existe en la Cartera o un texto no numérico, when el Ejecutivo de cuentas lo busca, then ve el mensaje correspondiente y ningún resultado, sin errores no controlados.
- **AC-04** (BF-01..BF-04): Given un cliente con Balance $100,000, 2 productos, con tarjeta y Probabilidad de fuga 0.10, con los parámetros base, when el Ejecutivo de cuentas busca su identificador, then ve la Ganancia neta esperada de Bonificación transaccional −$8.60, ninguna positiva, y la Decisión de retención "Sin Acción Requerida".

## Out of scope
- Búsqueda por apellido.
- Explicación de la Probabilidad de fuga (US-007).

## Open questions
- [x] **Q-01:** Ver SRS/Q-02: etiqueta de los clientes sin Incentivo rentable en los Segmentos D y E. → **A:** SRS/BR-02.
- [x] **Q-02:** Ver SRS/Q-03: si el Buscador usa los parámetros del Simulador o los valores base. → **A:** Parámetros vigentes (SRS/BR-08).
