---
id: US-012
title: Ajustar los parámetros del margen
status: done
priority: low
epic: EP-004
---

# US-012: Ajustar los parámetros del margen

## Story
**As a** Dirección de Estrategia
**I want** cambiar el Spread, la Comisión por producto, la Comisión por tarjeta y el Costo de servicio
**so that** pueda ver cómo cambian las Decisiones de retención si el Margen del cliente real difiere del supuesto.

## Context
El dataset no trae márgenes ni comisiones, así que el Margen del cliente es un supuesto (SRS/BR-03). Poder ajustarlo hace visible qué tan sensibles son las decisiones a ese supuesto.

## Actors
- **Primary:** Dirección de Estrategia.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** La Dirección de Estrategia está en el Simulador de parámetros.

## Basic flow
- **BF-01:** La Dirección de Estrategia cambia un parámetro del Margen del cliente.
- **BF-02:** System valida el nuevo valor.
- **BF-03:** System recalcula el Margen del cliente de cada cliente, la mediana que separa los niveles de valor Medio y Superior (SRS/BR-05), el Segmento y la Decisión de retención de cada cliente, y los indicadores del Panel de cartera.

## Alternate flows
- **AF-01** (from BF-02): If el Spread está fuera del rango 0% a 100% o una comisión o el Costo de servicio son negativos, then System muestra el rango permitido y conserva el valor anterior. → End.

## Post-conditions
- **POST-01:** Los Márgenes del cliente, los Segmentos, las Decisiones de retención y los indicadores reflejan los nuevos parámetros.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-03): Given un cliente con Balance $100,000, 2 productos, con tarjeta y Probabilidad de fuga 0.80, con Decisión de retención "Exoneración de comisiones", when la Dirección de Estrategia baja el Spread a 0%, then su Margen del cliente pasa a $70 y su Decisión de retención pasa a "Salida Permitida".
- **AC-02** (AF-01): Given el Simulador de parámetros, when la Dirección de Estrategia ingresa un Costo de servicio de −$10, then ve el rango permitido y los indicadores no cambian.

## Out of scope
- Cambiar la fórmula del Margen del cliente.

## Open questions
- [x] **Q-01:** Al cambiar los parámetros, la mediana que separa los niveles de valor Medio y Superior (SRS/BR-05), ¿se recalcula con los nuevos márgenes? → **A:** Sí (BF-03).
