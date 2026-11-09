---
id: US-009
title: Ver la matriz de decisión por segmento
status: ready
priority: medium
epic: EP-003
---

# US-009: Ver la matriz de decisión por segmento

## Story
**As a** Dirección de Estrategia
**I want** ver cuántos clientes hay en cada Segmento y qué Decisiones de retención reciben
**so that** entienda dónde se concentra el riesgo y en qué se gasta el presupuesto.

## Context
La plantilla del Informe ejecutivo incluye una "Matriz de Decisión Comercial y Rentabilidad" con los Segmentos A a D. Se agregó el Segmento E (riesgo intermedio) para que la matriz cubra a todos los clientes (SRS/BR-05).

## Actors
- **Primary:** Dirección de Estrategia.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** La Dirección de Estrategia está en el Panel de cartera.

## Basic flow
- **BF-01:** System asigna a cada cliente de la Cartera su Segmento según SRS/BR-05.
- **BF-02:** System muestra una fila por Segmento con: número de clientes, rango de Probabilidad de fuga, nivel de valor, número de clientes por Decisión de retención, Inversión en retención y suma de la Ganancia neta esperada de los Incentivos asignados.

## Alternate flows
- **AF-01** (from BF-02): If un Segmento no tiene clientes, then su fila se muestra con 0 clientes y montos en $0.00. → End.

## Post-conditions
- **POST-01:** La Dirección de Estrategia ve la matriz de segmentos de toda la Cartera.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-02): Given la Cartera completa, when se muestra la matriz, then la suma de los clientes de los Segmentos A a E es igual al Volumen de clientes analizados y la suma de su Inversión en retención es igual a la del Panel de cartera.
- **AC-02** (BF-01): Given un cliente con Probabilidad de fuga 0.70 y Margen del cliente −$10, when se muestra la matriz, then ese cliente cuenta en el Segmento C; y un cliente con Probabilidad de fuga 0.40 cuenta en el Segmento E.
- **AC-03** (AF-01): Given una Cartera sin clientes con Probabilidad de fuga ≥ 0.65, when se muestra la matriz, then las filas A, B y C aparecen con 0 clientes y $0.00.

## Out of scope
- Detalle de los clientes de cada Segmento.

## Open questions
- [x] **Q-01:** La plantilla tiene una columna "Incentivo asignado" por Segmento, pero la decisión es por cliente. ¿Basta con el número de clientes por Decisión de retención, o se muestra el Incentivo más frecuente del Segmento? → **A:** Número de clientes por Decisión de retención (BF-02).
