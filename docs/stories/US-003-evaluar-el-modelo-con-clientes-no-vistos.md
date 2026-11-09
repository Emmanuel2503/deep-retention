---
id: US-003
title: Evaluar el modelo con clientes no vistos
status: in-progress
priority: high
epic: EP-001
---

# US-003: Evaluar el modelo con clientes no vistos

## Story
**As a** Analista de datos
**I want** medir qué tan bien la red distingue y estima la fuga en Clientes de prueba
**so that** la Dirección de Estrategia pueda confiar en la Probabilidad de fuga que usa la regla financiera.

## Context
El Informe ejecutivo exige reportar ROC-AUC, Precision-Recall AUC y precisión de calibración. Como la ponderación de clases infla las probabilidades y la Ganancia neta esperada las usa directamente, hay que demostrar que la calibración las corrige.

## Actors
- **Primary:** Analista de datos.
- **Secondary:** Dirección de Estrategia (lee las métricas en el Informe ejecutivo).

## Pre-conditions
- **PRE-01:** El modelo está entrenado y guardado (US-002).

## Basic flow
- **BF-01:** El Analista de datos ejecuta la evaluación.
- **BF-02:** System calcula ROC-AUC y PR-AUC sobre los Clientes de prueba.
- **BF-03:** System calcula el Brier score y la curva de fiabilidad sobre los Clientes de prueba, antes y después de calibrar.
- **BF-04:** System guarda las métricas y las figuras en el repositorio.

## Alternate flows
- **AF-01** (from BF-03): If ROC-AUC < 0.80, PR-AUC < 0.55 o el Brier score calibrado es mayor que el sin calibrar, then System marca la evaluación como "no aceptada"; los artefactos no se versionan y el Analista de datos corrige el entrenamiento y lo repite antes de que empiece cualquier slice que dependa del modelo. → End.

## Post-conditions
- **POST-01:** Las métricas sobre los Clientes de prueba están guardadas y disponibles para la aplicación y el Informe ejecutivo.

## Business rules
- **BR-01:** El modelo se acepta solo si, sobre los Clientes de prueba, ROC-AUC ≥ 0.80, PR-AUC ≥ 0.55 (SRS/OBJ-01) y el Brier score calibrado ≤ el sin calibrar (SRS/OBJ-02).

## Acceptance criteria
- **AC-01** (BF-01..BF-02): Given el modelo guardado, when se ejecuta la evaluación, then se guardan ROC-AUC y PR-AUC calculados sobre los 1,500 Clientes de prueba, y ningún cliente de entrenamiento o validación participa en el cálculo.
- **AC-02** (BF-03..BF-04): Given el modelo guardado, when se ejecuta la evaluación, then se guardan el Brier score antes y después de calibrar y una figura de la curva de fiabilidad con ambas curvas.
- **AC-03** (AF-01): Given un modelo con ROC-AUC 0.78 sobre los Clientes de prueba, o uno con ROC-AUC 0.85, PR-AUC 0.60 y Brier calibrado 0.15 frente a 0.12 sin calibrar, when se ejecuta la evaluación, then la evaluación queda marcada como "no aceptada".

## Out of scope
- Análisis de errores por subgrupo.

## Open questions
- [x] **Q-01:** Ver SRS/Q-01: valores mínimos aceptables de ROC-AUC y PR-AUC. → **A:** ROC-AUC ≥ 0.80 y PR-AUC ≥ 0.55 (SRS/OBJ-01).
