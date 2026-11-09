---
id: EP-004
title: Simular parámetros de campaña
status: ready
priority: medium
requirements: [FR-05]
---

# EP-004: Simular parámetros de campaña

## Goal
La Dirección de Estrategia ajusta en el Simulador de parámetros los costos y la Efectividad de los Incentivos y los parámetros del Margen del cliente, y ve de inmediato el impacto en las Decisiones de retención y en la rentabilidad de la Cartera. Así puede evaluar escenarios de campaña antes de aprobarlos.

## Actors
- Dirección de Estrategia (main actor).

## Shared business rules
- **BR-01:** Al cambiar cualquier parámetro, las Decisiones de retención, los Segmentos y los indicadores del Panel de cartera se recalculan sin reentrenar la red; la Probabilidad de fuga de cada cliente no cambia.
- **BR-02:** Los valores iniciales de todos los parámetros son los valores base de SRS/BR-03 y SRS/BR-04.
- **BR-03:** Un valor inválido no se aplica y se muestra un mensaje que indica el rango permitido.
- **BR-04:** Los parámetros ajustados duran solo la sesión: al abrir la aplicación vuelven a los valores base, y en cualquier momento se pueden restablecer los valores base.

## Done when
- [ ] **DW-01:** Al cambiar el costo o la Efectividad de un Incentivo, la Inversión en retención y el ROI del Panel de cartera cambian según SRS/BR-06.
- [ ] **DW-02:** Al cambiar un parámetro del Margen del cliente, los Segmentos y las Decisiones de retención se recalculan.

## Out of scope
- Guardar escenarios con nombre o compararlos lado a lado.
- Agregar o quitar Incentivos del catálogo.

## Open questions
- [x] **Q-01:** ¿Los parámetros ajustados se conservan al cerrar la aplicación, o vuelven a los valores base en cada sesión? → **A:** Solo duran la sesión (BR-04).
- [x] **Q-02:** ¿Hay un botón para restablecer los valores base? → **A:** Sí (BR-04).
