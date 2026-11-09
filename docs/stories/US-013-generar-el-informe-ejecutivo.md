---
id: US-013
title: Generar el informe ejecutivo
status: ready
priority: medium
epic: EP-005
---

# US-013: Generar el informe ejecutivo

## Story
**As a** Analista de datos
**I want** generar el Informe ejecutivo en PDF con las cifras y figuras del proyecto
**so that** la Dirección de Estrategia evalúe el sistema con un documento gerencial y no técnico.

## Context
El enunciado incluye una plantilla de Informe ejecutivo de cinco secciones, y la rúbrica valora métricas claras de ROI, balance salvado e interpretabilidad, con enfoque gerencial.

## Actors
- **Primary:** Analista de datos.
- **Secondary:** Dirección de Estrategia (lectora).

## Pre-conditions
- **PRE-01:** Las métricas del modelo (US-003), los Factores de fuga (US-004) y los indicadores de la Cartera con parámetros base (US-008, US-009) están disponibles.

## Basic flow
- **BF-01:** El Analista de datos completa el texto del informe siguiendo la plantilla del enunciado.
- **BF-02:** El Analista de datos genera el PDF.
- **BF-03:** System produce el PDF en `reports/` con las cifras, tablas y figuras del proyecto.

## Alternate flows
None.

## Post-conditions
- **POST-01:** El Informe ejecutivo en PDF está en `reports/` y enlazado desde el README.

## Business rules
- **BR-01:** El informe contiene las secciones: 1. Resumen de impacto financiero y retorno; 2. Arquitectura de la solución y diagnóstico de fuga; 3. Matriz de decisión comercial y rentabilidad; 4. Operación de la aplicación en sucursales; 5. Conclusiones y próximos pasos.
- **BR-02:** El informe documenta los supuestos financieros (SRS/BR-03 y SRS/BR-04), incluido el horizonte: el Margen del cliente es anual, el Costo del Incentivo se paga una vez y se asume que la fuga de `Exited` ocurre dentro de ese año; y la exclusión de `Complain` por fuga de datos. La sección 2 menciona como limitación que SHAP perturba por separado las columnas one-hot y puede evaluar combinaciones imposibles (por ejemplo, dos países a la vez).
- **BR-03:** Mantenimiento del modelo: los datos se actualizan y la red se reentrena cada trimestre, o antes si el ROC-AUC sobre clientes nuevos cae más de 0.05 respecto del reportado.
- **BR-04:** Próximos pasos: prueba piloto de 3 meses en 2 o 3 sucursales con un grupo de control que no recibe Incentivos; despliegue general solo si el ROI real del piloto es mayor que 0.
- **BR-05:** Procedimiento del Ejecutivo de cuentas en sucursal: 1) buscar al cliente por su identificador, o ingresarlo por formulario si es nuevo; 2) revisar la Probabilidad de fuga, la Decisión de retención y los Factores de fuga; 3) si hay Incentivo, ofrecerlo usando los Factores de fuga para orientar la conversación; 4) si la decisión es Salida Permitida o Sin Acción Requerida, dar atención ordinaria sin gasto de retención; 5) registrar el resultado fuera del sistema para el piloto.
- **BR-06:** La sección 3 explica, con cifras de la Cartera, tres consecuencias de la regla financiera que difieren de la plantilla del enunciado: (a) clientes del Segmento D reciben Incentivo cuando `Probabilidad de fuga > Costo / (Efectividad × Margen del cliente)`, por eso su fila puede tener inversión; (b) la asignación "según el perfil" sale de la fórmula y no de reglas de elegibilidad: Gestor VIP solo supera a Exoneración de comisiones si `Probabilidad de fuga × Margen del cliente > $3,500`, lo que en la práctica lo limita a clientes de margen alto y riesgo alto; (c) el Segmento C es pequeño porque solo el Margen del cliente ≤ 0 es Bajo/Deficitario (el número de clientes sale de la matriz de segmentos calculada con la Cartera puntuada), y el nivel Medio incluye clientes con saldo 0.
- **BR-07:** La sección 1 reporta la cifra de la plantilla "Monto Total de Capital en Riesgo Crítico" con el Capital en riesgo crítico, agrega junto al ROI el "ROI realizado con la Efectividad supuesta" sobre los Clientes de prueba, y aclara que el ROI es > 0 por construcción (SRS/BR-02) y que el ROI realizado usa el abandono real pero no una Efectividad observada.

## Acceptance criteria
- **AC-01** (BF-01..BF-03): Given las métricas y los indicadores con parámetros base, when se genera el informe, then el PDF contiene las cinco secciones de BR-01, sin campos de la plantilla sin completar, y su Capital en riesgo crítico, Capital rescatable, Inversión en retención y ROI coinciden con los del Panel de cartera con los parámetros base, y su ROI realizado con el del Panel filtrado a los Clientes de prueba.
- **AC-02** (BF-03): Given el informe generado, when se revisa la sección 2, then incluye ROC-AUC, PR-AUC y Brier score sobre los Clientes de prueba, los tres Factores de fuga principales y la limitación de SHAP con las variables one-hot.

- **AC-03** (BF-01, BR-03..BR-05): Given el informe generado, when se revisan las secciones 4 y 5, then contienen el procedimiento de 5 pasos, la frecuencia de reentrenamiento trimestral con su condición de adelanto y el plan piloto de 3 meses con grupo de control.
- **AC-04** (BF-01, BR-06, BR-07): Given el informe generado, when se revisan las secciones 1 y 3, then la sección 3 explica la inversión del Segmento D, la asignación de Gestor VIP y el tamaño del Segmento C con cifras de la Cartera, y la sección 1 incluye el ROI realizado y la nota de que el ROI es > 0 por construcción.

## Out of scope
- Versión en inglés del informe.

## Open questions
- [x] **Q-01:** Ver SRS/Q-04 y SRS/Q-05: contenido de "Mantenimiento del Modelo" y de la prueba piloto. → **A:** BR-03 y BR-04.
- [x] **Q-02:** ¿Qué procedimiento paso a paso sigue el Ejecutivo de cuentas en sucursal (sección 4)? → **A:** BR-05.
