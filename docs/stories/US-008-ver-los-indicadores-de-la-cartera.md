---
id: US-008
title: Ver los indicadores de la cartera
status: ready
priority: high
epic: EP-003
---

# US-008: Ver los indicadores de la cartera

## Story
**As a** Dirección de Estrategia
**I want** ver el Capital en riesgo, el Capital rescatable, la Inversión en retención y el ROI de la Cartera
**so that** pueda justificar el presupuesto de retención ante la Junta Directiva.

## Context
El enunciado pide un Panel de cartera con el balance total en riesgo, la efectividad proyectada de las intervenciones y el dinero consolidado a rescatar; el Informe ejecutivo pide las mismas cifras en su sección 1.

## Actors
- **Primary:** Dirección de Estrategia.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** Cada cliente de la Cartera tiene una Probabilidad de fuga.

## Basic flow
- **BF-01:** La Dirección de Estrategia abre el Panel de cartera.
- **BF-02:** System calcula la Decisión de retención de cada cliente de la Cartera.
- **BF-03:** System muestra el Volumen de clientes analizados, el Capital en riesgo, el Capital en riesgo crítico, el Capital rescatable, la Inversión en retención, el Margen salvado, el ROI, las Fugas evitadas esperadas con su porcentaje (EP-003/BR-03) y el número de clientes por Decisión de retención.

## Alternate flows
- **AF-01** (from BF-03): If ningún cliente tiene Incentivo asignado, then System muestra Inversión en retención $0.00 y el ROI como "N/A". → End.

## Post-conditions
- **POST-01:** La Dirección de Estrategia ve los indicadores consolidados de la Cartera.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-03): Given una Cartera con dos clientes, uno con Balance $100,000, 2 productos, con tarjeta y Probabilidad de fuga 0.80, y otro con Balance $0, 1 producto, sin tarjeta y Probabilidad de fuga 0.50, con los parámetros base, when la Dirección de Estrategia abre el Panel de cartera, then ve Volumen 2, Capital en riesgo $80,000, Capital en riesgo crítico $100,000, Capital rescatable $24,000, Inversión en retención $150, Margen salvado $496.80, ROI 231.2%, Fugas evitadas esperadas 0.24 (30% de 0.80), 1 cliente con Exoneración de comisiones y 1 con Salida Permitida.
- **AC-02** (AF-01): Given una Cartera donde ningún cliente tiene Incentivo rentable, when la Dirección de Estrategia abre el Panel de cartera, then ve Inversión en retención $0.00 y el ROI como "N/A", sin errores.
- **AC-03** (BF-03): Given la Cartera completa del dataset, when la Dirección de Estrategia abre el Panel de cartera, then ve Volumen 10,000 y la nota de que el 85% de los clientes se usó para entrenar o calibrar la red.

## Out of scope
- Desglose de los indicadores por país o género.

## Open questions
- [x] **Q-01:** Ver EP-003/Q-01: definición de la "efectividad proyectada de las intervenciones". → **A:** Fugas evitadas esperadas (EP-003/BR-03).
- [x] **Q-02:** ¿Cómo se muestra el ROI cuando no hay inversión: "N/A", "—" u otro texto? → **A:** "N/A" (AF-01).
