---
id: EP-001
title: Estimar el riesgo de fuga
status: in-progress
priority: high
requirements: [FR-01, FR-02]
---

# EP-001: Estimar el riesgo de fuga

## Goal
El Analista de datos dispone de una red neuronal entrenada que asigna a cada cliente una Probabilidad de fuga confiable, y de una explicación de los Factores de fuga que la justifican. Sin esta probabilidad no se puede calcular la Ganancia neta esperada, y sin la explicación la Dirección de Estrategia no puede confiar en las decisiones de la red.

## Actors
- Analista de datos (main actor).
- Dirección de Estrategia: recibe las métricas y los Factores de fuga en el Informe ejecutivo.

## Shared business rules
- **BR-01:** Las métricas de desempeño del modelo se calculan solo sobre los Clientes de prueba.
- **BR-02:** Ninguna variable identificadora ni con fuga de datos se usa como entrada de la red (ver SRS/TR-03).

## Done when
- [ ] **DW-01:** Cada uno de los 10,000 clientes tiene una Probabilidad de fuga entre 0 y 1 producida por la red guardada en el repositorio.
- [ ] **DW-02:** ROC-AUC, PR-AUC y Brier score sobre los Clientes de prueba están publicados y cumplen SRS/OBJ-01 y SRS/OBJ-02.
- [ ] **DW-03:** Los tres Factores de fuga principales están identificados con evidencia de explicabilidad.

## Out of scope
- Comparación con otros modelos (árboles, regresión logística).
- Búsqueda exhaustiva de hiperparámetros.
- Explicación por cliente en la aplicación (EP-002).

## Open questions
None.
