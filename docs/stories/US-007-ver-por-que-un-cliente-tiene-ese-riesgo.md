---
id: US-007
title: Ver por qué un cliente tiene ese riesgo
status: ready
priority: medium
epic: EP-002
---

# US-007: Ver por qué un cliente tiene ese riesgo

## Story
**As a** Ejecutivo de cuentas
**I want** ver qué características del cliente aumentan o reducen su Probabilidad de fuga
**so that** pueda explicarle la recomendación y orientar la conversación con el cliente.

## Context
La rúbrica pide técnicas de interpretabilidad para justificar las decisiones de la red. Mostrar la explicación por cliente evita que la Probabilidad de fuga sea una caja negra para el Ejecutivo de cuentas.

## Actors
- **Primary:** Ejecutivo de cuentas.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** El Ejecutivo de cuentas consultó a un cliente existente (US-005) o nuevo (US-006).

## Basic flow
- **BF-01:** System calcula la contribución de cada variable del cliente a su Probabilidad de fuga.
- **BF-02:** System muestra un gráfico que parte de la Probabilidad de fuga media de los clientes de referencia y suma la contribución de cada variable hasta llegar a la Probabilidad de fuga del cliente, ordenadas de mayor a menor efecto.

## Alternate flows
None.

## Post-conditions
- **POST-01:** El Ejecutivo de cuentas ve las variables que más explican el riesgo del cliente.

## Business rules
- **BR-01:** Cada variable se muestra con el valor del cliente (por ejemplo, "Edad = 52"), no con su valor transformado.
- **BR-02:** El gráfico explica la Probabilidad de fuga calibrada (SRS/BR-07): la Probabilidad de fuga media de referencia más la suma de las contribuciones es igual a la Probabilidad de fuga del cliente.

## Acceptance criteria
- **AC-01** (BF-01..BF-02): Given un cliente consultado por su identificador o ingresado por formulario, when se muestran sus resultados, then aparece un gráfico con las contribuciones de sus variables, cada una etiquetada con el valor original del cliente, la variable de mayor efecto aparece primera, y la Probabilidad de fuga media de referencia más la suma de las contribuciones es igual (± 0.01) a la Probabilidad de fuga que se muestra del cliente.

## Out of scope
- Explicaciones en texto generadas automáticamente.

## Open questions
- [x] **Q-01:** ¿La explicación se muestra también para los clientes nuevos ingresados por formulario (US-006)? → **A:** Sí (PRE-01).
- [x] **Q-02:** La explicación, ¿se expresa sobre la Probabilidad de fuga calibrada o sobre la salida sin calibrar de la red? → **A:** Sobre la calibrada (BR-02): explicar la salida sin calibrar no conserva en general el orden de los factores ni llega a la probabilidad que se muestra.
