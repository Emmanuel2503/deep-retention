---
id: US-002
title: Entrenar y exportar el modelo de fuga
status: ready
priority: high
epic: EP-001
---

# US-002: Entrenar y exportar el modelo de fuga

## Story
**As a** Analista de datos
**I want** entrenar la red con las variables de entrada y guardar el modelo resultante en el repositorio
**so that** la aplicación pueda estimar la Probabilidad de fuga de cualquier cliente sin volver a entrenar.

## Context
La Junta Directiva exige un motor basado en redes neuronales. La rúbrica pide preparación rigurosa de los datos, control del sobreajuste, manejo del desbalance (solo el 20.4% abandona) y pesos guardados del modelo.

## Actors
- **Primary:** Analista de datos.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** La lista de variables de entrada está definida (US-001).

## Basic flow
- **BF-01:** El Analista de datos inicia el entrenamiento.
- **BF-02:** System divide la Cartera en entrenamiento, validación y prueba.
- **BF-03:** System entrena la red compensando el desbalance entre clientes que se van y que permanecen.
- **BF-04:** System detiene el entrenamiento cuando la pérdida de validación deja de mejorar.
- **BF-05:** System calibra la salida de la red con la partición de validación.
- **BF-06:** System guarda en el repositorio el modelo, la preparación de datos y la calibración.

## Alternate flows
None.

## Post-conditions
- **POST-01:** El repositorio contiene todo lo necesario para estimar la Probabilidad de fuga de un cliente nuevo sin reentrenar.

## Business rules
- **BR-01:** Las particiones son 70% entrenamiento, 15% validación y 15% prueba, con la misma proporción de abandono en cada una.

## Acceptance criteria
- **AC-01** (BF-02): Given el dataset de 10,000 clientes, when se ejecuta el entrenamiento dos veces, then ambas ejecuciones producen particiones de 7,000, 1,500 y 1,500 clientes con exactamente los mismos clientes, y cada partición tiene una tasa de abandono de 20.4% ± 0.5 puntos.
- **AC-02** (BF-03..BF-04): Given un entrenamiento en curso, when la pérdida de validación no mejora durante el número configurado de épocas (entre 10 y 15), then el entrenamiento se detiene y el modelo conserva los pesos de la mejor época.
- **AC-03** (BF-05..BF-06): Given un entrenamiento terminado, when se cargan los archivos guardados sin volver a entrenar, then cada uno de los 10,000 clientes obtiene una Probabilidad de fuga entre 0 y 1.

## Out of scope
- Búsqueda de hiperparámetros.
- Medición del desempeño (US-003).

## Open questions
None.
