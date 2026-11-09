---
id: US-011
title: Ajustar costo y efectividad de los incentivos
status: ready
priority: medium
epic: EP-004
---

# US-011: Ajustar costo y efectividad de los incentivos

## Story
**As a** Dirección de Estrategia
**I want** cambiar el Costo del Incentivo y la Efectividad de cada Incentivo
**so that** pueda proyectar el impacto de una campaña en la rentabilidad de la Cartera antes de aprobarla.

## Context
El enunciado pide un Simulador de parámetros para ajustar los costos de las campañas y proyectar el impacto en la rentabilidad neta.

## Actors
- **Primary:** Dirección de Estrategia.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** La Dirección de Estrategia está en el Simulador de parámetros.

## Basic flow
- **BF-01:** La Dirección de Estrategia cambia el Costo del Incentivo o la Efectividad de un Incentivo.
- **BF-02:** System valida el nuevo valor.
- **BF-03:** System recalcula las Decisiones de retención de la Cartera y los indicadores del Panel de cartera.
- **BF-04:** System muestra los indicadores actualizados.

## Alternate flows
- **AF-01** (from BF-02): If el Costo del Incentivo es negativo o la Efectividad está fuera del rango 0% a 100%, then System muestra el rango permitido y conserva el valor anterior. → End.
- **AF-02** (from BF-01): If la Dirección de Estrategia pide restablecer los valores base, then System repone todos los parámetros del Simulador de parámetros (Incentivos y Margen del cliente) a los valores base. → Resume at BF-03.

## Post-conditions
- **POST-01:** Las Decisiones de retención y los indicadores reflejan los nuevos parámetros.

## Business rules
None.

## Acceptance criteria
- **AC-01** (BF-01..BF-04): Given un cliente con Balance $100,000, 2 productos, con tarjeta y Probabilidad de fuga 0.80, cuya Decisión de retención con los parámetros base es "Exoneración de comisiones", when la Dirección de Estrategia sube el Costo de Exoneración de comisiones a $400, then su Decisión de retención pasa a "Bonificación transaccional" (Ganancia neta esperada $281.20 frente a $96.80) y la Inversión en retención y el ROI se recalculan.
- **AC-02** (AF-01): Given el Simulador de parámetros, when la Dirección de Estrategia ingresa una Efectividad de 120%, then ve el rango permitido 0% a 100% y los indicadores no cambian.

- **AC-03** (AF-02): Given el Costo de Exoneración de comisiones en $400 y el Spread en 0%, when la Dirección de Estrategia restablece los valores base, then el Costo vuelve a $150, el Spread a 2% y los indicadores vuelven a los de los parámetros base.
- **AC-04** (EP-004/BR-04): Given parámetros cambiados en una sesión, when se abre la aplicación en una sesión nueva, then todos los parámetros tienen los valores base.

## Out of scope
- Agregar nuevos Incentivos al catálogo.

## Open questions
- [x] **Q-01:** Ver EP-004/Q-01 y EP-004/Q-02: persistencia de los parámetros y botón para restablecer. → **A:** EP-004/BR-04 (AF-02).
