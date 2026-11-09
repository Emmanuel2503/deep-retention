---
id: EP-005
title: Emitir el informe ejecutivo
status: ready
priority: medium
requirements: [FR-06]
---

# EP-005: Emitir el informe ejecutivo

## Goal
La Dirección de Estrategia recibe un Informe ejecutivo en PDF, con enfoque gerencial, que resume el impacto financiero, la arquitectura de la red, los Factores de fuga, la matriz de segmentos, la operación en sucursales y los próximos pasos. Es el entregable con el que la Junta Directiva evalúa el sistema.

## Actors
- Analista de datos (main actor): redacta y genera el informe.
- Dirección de Estrategia: lo lee.

## Shared business rules
- **BR-01:** Las cifras del informe se calculan con los parámetros base (SRS/BR-03, SRS/BR-04) y deben coincidir con las del Panel de cartera con esos mismos parámetros; el ROI realizado, con las del Panel filtrado a los Clientes de prueba.

## Done when
- [ ] **DW-01:** Existe un PDF en `reports/`, enlazado desde el README, con las cinco secciones de la plantilla del enunciado completas.

## Out of scope
- Generación del informe desde la aplicación.

## Open questions
None.
