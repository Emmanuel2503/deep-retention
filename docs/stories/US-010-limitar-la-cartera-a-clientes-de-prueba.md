---
id: US-010
title: Limitar la cartera a clientes de prueba
status: ready
priority: low
epic: EP-003
---

# US-010: Limitar la cartera a clientes de prueba

## Story
**As a** Dirección de Estrategia
**I want** ver los indicadores calculados solo con los Clientes de prueba
**so that** pueda comparar las cifras de la Cartera completa con las de clientes que la red nunca vio.

## Context
La Cartera completa incluye al 85% de clientes usados para entrenar o calibrar la red, cuyas Probabilidades de fuga son más confiadas que las de clientes no vistos. El filtro permite una lectura metodológicamente honesta y es el único lugar donde se puede medir el ROI realizado (SRS/OBJ-03), porque usa el abandono real de clientes que la red no vio.

## Actors
- **Primary:** Dirección de Estrategia.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** La Dirección de Estrategia está en el Panel de cartera.

## Basic flow
- **BF-01:** La Dirección de Estrategia activa la opción "Solo clientes de prueba".
- **BF-02:** System recalcula todos los indicadores y la matriz de segmentos solo con los Clientes de prueba, y muestra además el ROI realizado (SRS/BR-06).

## Alternate flows
- **AF-01** (from BF-02): If la Dirección de Estrategia desactiva la opción, then System vuelve a mostrar la Cartera completa, sin el ROI realizado. → End.
- **AF-02** (from BF-02): If ningún Cliente de prueba tiene Incentivo asignado, then System muestra el ROI realizado como "N/A". → End.

## Post-conditions
- **POST-01:** Los indicadores y la matriz corresponden a los Clientes de prueba.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-02): Given el Panel de cartera con la Cartera completa, when la Dirección de Estrategia activa "Solo clientes de prueba", then el Volumen de clientes analizados es 1,500 y los indicadores y la matriz se recalculan con esos clientes.
- **AC-02** (AF-01): Given la opción activada, when la Dirección de Estrategia la desactiva, then el Volumen vuelve a 10,000 con los mismos indicadores que antes de activarla.
- **AC-03** (BF-02, AF-02): Given dos Clientes de prueba, uno con Balance $100,000, 2 productos, con tarjeta, Probabilidad de fuga 0.80 y que abandonó (`Exited` = 1), y otro con Balance $0, 1 producto, sin tarjeta y Probabilidad de fuga 0.50, con los parámetros base, when la Dirección de Estrategia activa "Solo clientes de prueba", then ve ROI realizado 314.0% ((0.30 × 2,070 − 150) / 150); y si ningún Cliente de prueba tiene Incentivo, ve "N/A".

## Out of scope
- Filtros por otras variables del cliente.

## Open questions
None.
