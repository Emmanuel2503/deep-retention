---
id: US-006
title: Evaluar un cliente nuevo ingresando sus datos
status: ready
priority: high
epic: EP-002
---

# US-006: Evaluar un cliente nuevo ingresando sus datos

## Story
**As a** Ejecutivo de cuentas
**I want** ingresar los datos de un cliente que no está en la Cartera
**so that** obtenga su Decisión de retención aunque no esté en el dataset.

## Context
La rúbrica penaliza las aplicaciones que fallan "al ingresar datos nuevos". El formulario permite evaluar cualquier cliente y demostrar que el canal de inferencia funciona con datos no vistos.

## Actors
- **Primary:** Ejecutivo de cuentas.
- **Secondary:** None.

## Pre-conditions
- **PRE-01:** El Ejecutivo de cuentas está en el Buscador por cliente, en el modo de cliente nuevo.

## Basic flow
- **BF-01:** El Ejecutivo de cuentas completa en el formulario cada variable de entrada de la red (US-001).
- **BF-02:** System valida que cada valor esté dentro de su rango permitido.
- **BF-03:** System estima la Probabilidad de fuga y calcula el Margen del cliente y la Ganancia neta esperada de cada Incentivo.
- **BF-04:** System muestra la Probabilidad de fuga, el Margen del cliente, la Ganancia neta esperada de cada Incentivo, el Segmento y la Decisión de retención.

## Alternate flows
- **AF-01** (from BF-02): If algún valor falta o está fuera de su rango, then System señala el campo, muestra el rango permitido y no calcula resultados. → Resume at BF-01.

## Post-conditions
- **POST-01:** El Ejecutivo de cuentas ve la Decisión de retención del cliente nuevo.

## Business rules
- **BR-01:** Las variables categóricas (`Geography`, `Gender`, `Card Type`) solo admiten los valores presentes en el dataset; `HasCrCard` e `IsActiveMember` solo admiten Sí (1) o No (0).
- **BR-02:** Los rangos permitidos son límites de negocio, no los observados en el dataset: CreditScore 300 a 850; Age 18 a 100; Tenure 0 a 50; Balance ≥ 0; NumOfProducts entero ≥ 1; EstimatedSalary ≥ 0; Satisfaction Score entero de 1 a 5; Point Earned ≥ 0. Valores dentro de estos límites se aceptan aunque no aparezcan en el dataset.

## Acceptance criteria
- **AC-01** (BF-01..BF-04): Given un formulario con Balance $250,000, 2 productos, con tarjeta y valores válidos en el resto de los campos, con los parámetros base, when el Ejecutivo de cuentas envía el formulario, then ve Margen del cliente $5,070, una Probabilidad de fuga entre 0 y 1, la Ganancia neta esperada de cada Incentivo según SRS/BR-01 y la Decisión de retención según SRS/BR-02.
- **AC-02** (AF-01): Given un formulario con Balance −100, when el Ejecutivo de cuentas lo envía, then ve un mensaje junto al campo Balance con el rango permitido, ningún resultado y ningún error no controlado.
- **AC-03** (BR-01): Given el campo `Geography`, when el Ejecutivo de cuentas lo despliega, then solo puede elegir France, Germany o Spain; y los campos `HasCrCard` e `IsActiveMember` solo permiten Sí o No.
- **AC-04** (BR-02): Given un formulario válido con NumOfProducts 6, when el Ejecutivo de cuentas lo envía, then el formulario se acepta y se muestran resultados; y con Age 17, then ve el rango permitido 18 a 100 y ningún resultado.

## Out of scope
- Guardar el cliente nuevo en la Cartera.

## Open questions
- [x] **Q-01:** ¿Cuáles son los rangos permitidos de cada variable numérica: el mínimo y máximo del dataset, o límites de negocio (por ejemplo, edad de 18 a 100)? → **A:** Límites de negocio (BR-02).
