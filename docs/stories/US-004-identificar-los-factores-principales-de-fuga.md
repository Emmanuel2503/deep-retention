---
id: US-004
title: Identificar los factores principales de fuga
status: in-progress
priority: medium
epic: EP-001
---

# US-004: Identificar los factores principales de fuga

## Story
**As a** Analista de datos
**I want** saber qué variables pesan más en la Probabilidad de fuga que estima la red
**so that** el Informe ejecutivo justifique las decisiones de la red con los tres Factores de fuga principales.

## Context
La plantilla del Informe ejecutivo pide los tres factores determinantes de abandono, y la rúbrica exige técnicas de interpretabilidad (como SHAP) para el nivel excelente.

## Actors
- **Primary:** Analista de datos.
- **Secondary:** Dirección de Estrategia (lee los factores en el Informe ejecutivo).

## Pre-conditions
- **PRE-01:** El modelo está entrenado y guardado (US-002).

## Basic flow
- **BF-01:** El Analista de datos ejecuta el análisis de explicabilidad sobre una muestra aleatoria, siempre la misma, de 500 Clientes de prueba.
- **BF-02:** System ordena las variables por su contribución media a la Probabilidad de fuga.
- **BF-03:** System guarda una figura resumen y la lista ordenada de Factores de fuga.

## Alternate flows
None.

## Post-conditions
- **POST-01:** La figura resumen y los tres Factores de fuga principales están disponibles para el Informe ejecutivo.

## Business rules
- **BR-01:** Las variables codificadas a partir de una misma categoría (por ejemplo, cada país de `Geography`) se reportan como una sola variable en la lista de Factores de fuga.

## Acceptance criteria
- **AC-01** (BF-01..BF-03): Given el modelo guardado, when se ejecuta el análisis de explicabilidad, then se guardan una figura resumen y una lista de variables ordenada de mayor a menor contribución, donde cada variable original aparece una sola vez.

## Out of scope
- Explicación por cliente (US-007).

## Open questions
- [x] **Q-01:** ¿De cuántos clientes es la muestra del análisis? Se habló de unos 500; falta confirmarlo. → **A:** 500 Clientes de prueba, muestra fija (BF-01).
