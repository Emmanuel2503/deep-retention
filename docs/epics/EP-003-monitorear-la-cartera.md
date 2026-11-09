---
id: EP-003
title: Monitorear la cartera
status: ready
priority: high
requirements: [FR-04]
---

# EP-003: Monitorear la cartera

## Goal
La Dirección de Estrategia ve en el Panel de cartera el Capital en riesgo, el Capital rescatable, la Inversión en retención y el ROI de toda la Cartera, y cómo se distribuyen los clientes por Segmento y Decisión de retención. Así puede justificar el presupuesto de retención con cifras consolidadas.

## Actors
- Dirección de Estrategia (main actor).

## Shared business rules
- **BR-01:** Por defecto la Cartera son los 10,000 clientes del dataset, y el Panel de cartera muestra una nota indicando que el 85% de ellos se usó para entrenar o calibrar la red (70% entrenamiento y 15% validación).
- **BR-02:** Todos los indicadores se calculan según SRS/BR-06 y se recalculan con los parámetros vigentes (SRS/BR-08).
- **BR-03:** La efectividad proyectada de las intervenciones se muestra como Fugas evitadas esperadas (Σ `Probabilidad de fuga × Efectividad` de los clientes con Incentivo) y como porcentaje de las fugas esperadas de esos mismos clientes (Σ `Probabilidad de fuga`).

## Done when
- [ ] **DW-01:** El Panel de cartera muestra el Volumen de clientes analizados, el Capital en riesgo, el Capital en riesgo crítico, el Capital rescatable, la Inversión en retención, las Fugas evitadas esperadas y el ROI, y coinciden con un cálculo independiente sobre los mismos datos.
- [ ] **DW-02:** La matriz de segmentos A a E cubre a todos los clientes de la Cartera.
- [ ] **DW-03:** La Dirección de Estrategia puede ver los mismos indicadores solo para los Clientes de prueba, junto con el ROI realizado (SRS/OBJ-03).

## Out of scope
- Evolución histórica de los indicadores.
- Exportar el panel a archivo.

## Open questions
- [x] **Q-01:** El enunciado pide monitorear la "efectividad proyectada de las intervenciones". ¿Cómo se define: Efectividad media ponderada de los Incentivos asignados, Margen salvado, u otro indicador? → **A:** Fugas evitadas esperadas (BR-03).
