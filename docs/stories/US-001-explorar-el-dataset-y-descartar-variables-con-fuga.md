---
id: US-001
title: Explorar el dataset y descartar variables con fuga
status: done
priority: high
epic: EP-001
---

# US-001: Explorar el dataset y descartar variables con fuga

## Story
**As a** Analista de datos
**I want** explorar el dataset de clientes y detectar las variables que delatan el resultado
**so that** la red aprenda solo de información disponible antes de que el cliente se vaya.

## Context
El dataset Bank Customer Churn trae 10,000 clientes con un 20.4% de abandono. La variable `Complain` tiene una correlación de 0.996 con `Exited`: si se usa, el modelo "acierta" sin aprender nada útil, y la rúbrica califica la fuga de datos como "Necesita mejora". Una correlación alta es solo una señal de alerta: una variable es fuga si se registra junto con la salida del cliente o después. El umbral 0.5 sirve porque ninguna variable legítima del dataset se acerca (la mayor es `Age`, 0.285). `Satisfaction Score`, `Card Type` y `Point Earned` no son habituales en este dataset, pero su correlación con `Exited` es casi nula (|r| < 0.03), así que se conservan como variables de entrada.

## Actors
- **Primary:** Analista de datos.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** El dataset está disponible en el repositorio.

## Basic flow
- **BF-01:** El Analista de datos abre la exploración del dataset.
- **BF-02:** System muestra el número de clientes, la tasa de abandono y la distribución de cada variable.
- **BF-03:** System muestra la correlación de cada variable con `Exited`.
- **BF-04:** El Analista de datos registra la lista final de variables de entrada y las excluidas, con el motivo de cada exclusión.

## Alternate flows
- **AF-01** (from BF-03): If una variable distinta de `Complain` tiene correlación > 0.5 con `Exited`, then se marca como fuga de datos y se agrega a las excluidas con su motivo. → Resume at BF-04.

## Post-conditions
- **POST-01:** Existe una lista documentada de variables de entrada y de variables excluidas con su motivo.

## Business rules
- **BR-01:** `RowNumber`, `CustomerId` y `Surname` se excluyen por ser identificadores; `Complain`, por fuga de datos.

## Acceptance criteria
- **AC-01** (BF-01..BF-02): Given el dataset del repositorio, when el Analista de datos ejecuta la exploración, then se muestran 10,000 clientes y una tasa de abandono del 20.4%.
- **AC-02** (BF-03..BF-04): Given el dataset del repositorio, when se completa la exploración, then la lista de excluidas contiene `RowNumber`, `CustomerId`, `Surname` y `Complain`, cada una con su motivo, y `Complain` aparece con correlación ≈ 0.996.
- **AC-03** (AF-01): Given una variable distinta de `Complain` con correlación > 0.5 con `Exited`, when se completa la exploración, then esa variable aparece en la lista de excluidas con el motivo "fuga de datos".

## Out of scope
- Ingeniería de nuevas variables.
- Limpieza de valores atípicos.

## Open questions
None.
