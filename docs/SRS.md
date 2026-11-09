---
title: Deep Retention
status: ready
updated: 2026-11-08
---

# Deep Retention: Software Requirements Specification

## 1. Project overview

### Problem
La retención indiscriminada de clientes está reduciendo el margen operativo del banco: se gasta presupuesto en promociones, bonificaciones y tasas preferenciales para clientes con saldos mínimos o que generan pérdidas netas. La Junta Directiva exige un motor predictivo basado en redes neuronales que estime el riesgo de fuga de cada cliente y que solo autorice un plan de retención cuando el cliente representa una ganancia neta para el banco tras descontar el costo del beneficio ofrecido.

### Users
- Ejecutivo de cuentas: gestor de sucursal que consulta a un cliente y aplica la Decisión de retención sugerida.
- Dirección de Estrategia: Dirección de Estrategia y Rentabilidad de Clientes; monitorea la Cartera, simula campañas y recibe el Informe ejecutivo.
- Analista de datos: miembro del equipo que explora los datos, entrena y evalúa el modelo y redacta el Informe ejecutivo.

### Scope
- Estimación de la Probabilidad de fuga de cada cliente con una red neuronal.
- Cálculo de la Ganancia neta esperada de cada Incentivo y asignación de la Decisión de retención.
- Explicación de los Factores de fuga, globales y por cliente.
- Aplicación interactiva con Buscador por cliente, Panel de cartera y Simulador de parámetros.
- Informe ejecutivo en PDF.

### Out of scope
- Ejecución real de campañas o envío de incentivos a clientes: el sistema solo recomienda.
- Integración con sistemas productivos del banco; la única fuente de datos es el dataset Bank Customer Churn (10,000 clientes).
- Autenticación y gestión de usuarios de la aplicación.
- Reentrenamiento automático del modelo.

### Glossary
See [Glossary](GLOSSARY.md).

## 2. Objectives

### 2.1 General objective
Destinar el presupuesto de retención solo a clientes cuya retención genera una ganancia neta esperada positiva para el banco, usando una Probabilidad de fuga estimada por una red neuronal.

### 2.2 Specific objectives
- **OBJ-01:** La red distingue a los clientes que se fugan de los que permanecen (medido por ROC-AUC y PR-AUC sobre los Clientes de prueba, target: ROC-AUC ≥ 0.80 y PR-AUC ≥ 0.55).
- **OBJ-02:** La Probabilidad de fuga es confiable como probabilidad (medido por Brier score sobre los Clientes de prueba, target: Brier de la probabilidad calibrada ≤ Brier de la salida sin calibrar).
- **OBJ-03:** La inversión en retención es rentable frente a las fugas reales, no solo frente a las estimadas por la red (medido por ROI realizado sobre los Clientes de prueba con los parámetros base (BR-06), target: > 0%).

## 3. Business rules
- **BR-01:** La Ganancia neta esperada de un Incentivo para un cliente es `Probabilidad de fuga × Efectividad del Incentivo × Margen del cliente − Costo del Incentivo`. Nunca se usa un umbral fijo de probabilidad (por ejemplo 0.5) para decidir.
- **BR-02:** La Decisión de retención de un cliente es el Incentivo con mayor Ganancia neta esperada, solo si esa ganancia es mayor que cero. Si ningún Incentivo tiene Ganancia neta esperada > 0, no se asigna gasto de retención y la decisión es Sin Acción Requerida si el cliente está en el Segmento D, o Salida Permitida en cualquier otro Segmento. Invariante: todo Incentivo asignado tiene Ganancia neta esperada > 0, así que el ROI de BR-06 es > 0 siempre que haya Inversión en retención; por eso no se usa como evidencia de rentabilidad (ver ROI realizado).
- **BR-03:** El Margen del cliente es anual y se calcula como `Balance × Spread + Productos × Comisión por producto + Tiene tarjeta × Comisión por tarjeta − Costo de servicio`. Valores base: Spread 2%, Comisión por producto $50, Comisión por tarjeta $30, Costo de servicio $60. El Margen del cliente puede ser negativo (cliente deficitario).
- **BR-04:** El catálogo de Incentivos y sus valores base son:

  | Incentivo | Costo | Efectividad |
  |---|---|---|
  | Gestor VIP y tarifa plana | $500 | 40% |
  | Exoneración de comisiones | $150 | 30% |
  | Bonificación transaccional | $50 | 20% |

  Todos los Incentivos están disponibles para todos los clientes; no hay reglas de elegibilidad por perfil.
- **BR-05:** El Segmento de un cliente es una etiqueta descriptiva: nunca decide si se asigna un Incentivo ni cuál; solo distingue, entre las decisiones sin gasto, Sin Acción Requerida (Segmento D) de Salida Permitida (BR-02). Un cliente de cualquier Segmento, incluido D, recibe un Incentivo si su Ganancia neta esperada es > 0. Nivel de valor: Bajo/Deficitario si Margen del cliente ≤ 0; Medio si es > 0 y ≤ la mediana del Margen del cliente positivo de la Cartera; Superior si es mayor que esa mediana. Segmentos:

  | Segmento | Probabilidad de fuga | Nivel de valor |
  |---|---|---|
  | A: Alto valor / Alto riesgo | ≥ 0.65 | Superior |
  | B: Medio / Riesgo moderado | ≥ 0.65 | Medio |
  | C: No rentable | ≥ 0.65 | Bajo/Deficitario |
  | D: Estable | < 0.30 | Cualquiera |
  | E: Riesgo intermedio | ≥ 0.30 y < 0.65 | Cualquiera |
- **BR-06:** Indicadores de la Cartera:
  - Capital en riesgo = Σ `Balance × Probabilidad de fuga` sobre todos los clientes de la Cartera.
  - Capital en riesgo crítico = Σ `Balance` sobre los clientes de la Cartera con Probabilidad de fuga ≥ 0.65.
  - Capital rescatable = Σ `Balance × Probabilidad de fuga × Efectividad` sobre los clientes con Incentivo asignado.
  - Inversión en retención = Σ Costo del Incentivo asignado.
  - Margen salvado = Σ `Probabilidad de fuga × Efectividad × Margen del cliente` sobre los clientes con Incentivo asignado.
  - ROI = `(Margen salvado − Inversión en retención) / Inversión en retención`.
  - ROI realizado = `(Σ Exited × Efectividad × Margen del cliente − Σ Costo del Incentivo) / Σ Costo del Incentivo`, sobre los Clientes de prueba con Incentivo asignado. Usa el abandono real (`Exited`) en lugar de la Probabilidad de fuga, así que puede ser negativo; la Efectividad sigue siendo la supuesta, así que no es un retorno observado: comprueba si la Probabilidad de fuga es buena en los clientes intervenidos.
- **BR-07:** La Probabilidad de fuga usada en todas las reglas es la probabilidad calibrada, nunca la salida sin calibrar de la red.
- **BR-08:** El Buscador por cliente, el Panel de cartera y la matriz de segmentos se calculan con los parámetros vigentes del Simulador de parámetros; al iniciar la aplicación, son los valores base de BR-03 y BR-04.
- **BR-09:** Los montos se muestran en dólares con dos decimales y la Probabilidad de fuga con dos decimales.

## 4. Functional requirements
- **FR-01:** Estimar la Probabilidad de fuga de cada cliente.
- **FR-02:** Explicar los Factores de fuga.
- **FR-03:** Consultar la Decisión de retención de un cliente.
- **FR-04:** Monitorear la Cartera.
- **FR-05:** Simular parámetros de campaña.
- **FR-06:** Emitir el Informe ejecutivo.

## 5. Non-functional requirements

### Maintainability
- **NFR-01:** La aplicación no importa ni ejecuta código de entrenamiento; solo usa el canal de inferencia y las reglas financieras. **Verified by:** revisión de las importaciones de la aplicación.
- **NFR-02:** Tras clonar el repositorio e instalar las dependencias declaradas, la aplicación arranca y responde sin reentrenar el modelo. **Verified by:** prueba manual en un entorno virtual limpio.
- **NFR-03:** Dos ejecuciones del entrenamiento producen exactamente las mismas particiones de clientes. **Verified by:** comparación de los identificadores de cada partición entre dos ejecuciones.

### Usability
- **NFR-04:** Ningún dato ingresado por el usuario provoca un error no controlado; los valores inválidos muestran un mensaje en español. **Verified by:** prueba manual con valores vacíos, negativos y fuera de rango.
- **NFR-05:** La interfaz de la aplicación y el Informe ejecutivo están en español. **Verified by:** revisión antes de la entrega.

## 6. Technological requirements
- **TR-01:** El modelo es un Perceptrón Multicapa en Keras: capa densa de 64 neuronas ReLU con Batch Normalization y Dropout 0.3, capa densa de 32 neuronas ReLU con Dropout 0.2, y salida de 1 neurona sigmoide. **Why:** el enunciado exige redes neuronales y recomienda esta arquitectura; Keras se eligió por su soporte directo de ponderación de clases y early stopping.
- **TR-02:** El entrenamiento se ejecuta en Jupyter notebooks en Google Colab que reutilizan los módulos del repositorio; los artefactos (pesos del modelo, preprocesador, calibrador y métricas) se guardan en `models/` y se versionan en el repositorio. El entorno local, Colab y Streamlit Community Cloud usan Python 3.12 (TensorFlow no admite Python 3.14 y Colab usa 3.12); el entorno local se crea en `venv/` con pip o con uv, y las dependencias se declaran solo en `requirements.txt`. `requirements.txt` fija con `==` las versiones de las librerías que serializan o leen artefactos (tensorflow, scikit-learn, joblib, numpy, pandas), iguales a las del entorno de Colab donde se entrenó, y el entrenamiento fija la semilla de Keras además de la de las particiones. **Why:** decisión del equipo; la rúbrica exige pesos guardados, y un pickle de scikit-learn o un `.keras` pueden no cargar con otra versión.
- **TR-03:** Se excluyen como entrada `RowNumber`, `CustomerId`, `Surname` y `Complain`; las variables numéricas se estandarizan y `Geography`, `Gender` y `Card Type` se codifican one-hot. Cualquier otra variable con correlación > 0.5 con `Exited` detectada en la exploración también se excluye. **Why:** `Complain` tiene correlación 0.996 con `Exited` (fuga de datos); el enunciado exige escalado y codificación categórica. Una correlación alta es solo una señal de alerta, no la definición de fuga; el umbral 0.5 sirve porque ninguna variable legítima del dataset se acerca (la mayor es `Age`, 0.285).
- **TR-04:** El desbalance se maneja con ponderación de clases en la pérdida y el entrenamiento se detiene tras 10 a 15 épocas sin mejora de la pérdida de validación. **Why:** exigido por el enunciado y la rúbrica.
- **TR-05:** Los clientes se dividen de forma estratificada y con semilla fija en entrenamiento (70%), validación (15%) y prueba (15%). La salida de la red se calibra con Platt sobre la validación. Las métricas técnicas se calculan solo sobre la prueba. **Why:** la ponderación de clases infla las probabilidades y la regla de BR-01 las usa directamente.
- **TR-06:** La explicabilidad se obtiene con SHAP sobre la Probabilidad de fuga calibrada (BR-07). **Why:** la rúbrica lo pide para el nivel excelente.
- **TR-07:** La aplicación se construye con Streamlit y se ejecuta en local y en Streamlit Community Cloud. **Why:** el enunciado recomienda Streamlit; el despliegue público deja un enlace para la evaluación.
- **TR-08:** El Informe ejecutivo se escribe en Markdown y se convierte a PDF con pandoc, con figuras exportadas desde los notebooks. **Why:** decisión del equipo.
- **TR-09:** El código se organiza en módulos separados de preprocesamiento, modelo, reglas financieras e inferencia, más un script de entrenamiento equivalente al notebook, y declara sus dependencias en `requirements.txt`. **Why:** la rúbrica exige código modular, inferencia separada del entrenamiento y archivo de dependencias.
- **TR-10:** No hay pruebas automatizadas; cada criterio de aceptación se verifica a mano según la tabla Tests de su slice (ADR-0006). **Why:** decisión del equipo por el plazo de entrega.

## 7. Open questions
- [x] **Q-01:** ¿Qué valores mínimos de ROC-AUC y PR-AUC sobre los Clientes de prueba se consideran aceptables? → **A:** ROC-AUC ≥ 0.80 y PR-AUC ≥ 0.55 (OBJ-01).
- [x] **Q-02:** Un cliente sin ningún Incentivo rentable y con Probabilidad de fuga < 0.30 (Segmento D), ¿se muestra como Salida Permitida o como "Sin Acción Requerida", como en la plantilla del informe? ¿Y uno del Segmento E? → **A:** Segmento D → Sin Acción Requerida; A, B, C y E → Salida Permitida (BR-02).
- [x] **Q-03:** ¿El Buscador por cliente usa también los parámetros vigentes del Simulador, o siempre los valores base? → **A:** Usa los parámetros vigentes (BR-08).
- [x] **Q-04:** ¿Con qué frecuencia se actualizan los datos y se reentrena la red (sección "Mantenimiento del Modelo" del informe)? → **A:** Contenido del Informe ejecutivo, ver US-013/BR-03.
- [x] **Q-05:** ¿Cuál es la estrategia y el cronograma de la prueba piloto (sección 5 del informe)? → **A:** Contenido del Informe ejecutivo, ver US-013/BR-04.
- [x] **Q-06:** El ROI de la Cartera y la proporción de Incentivos rentables se cumplen por construcción (BR-02). ¿Qué objetivo financiero sí puede fallar? → **A:** El ROI realizado sobre los Clientes de prueba con `Exited` real (OBJ-03, BR-06).
- [x] **Q-07:** Con la Ganancia neta esperada, clientes del Segmento D con margen alto reciben Incentivo, aunque la plantilla del enunciado pone D = "Sin Acción, $0.00". ¿Se bloquean? → **A:** No; manda la fórmula (BR-05) y el Informe ejecutivo lo explica (US-013/BR-06).
- [x] **Q-08:** Con los valores base, muy pocos clientes tienen Margen del cliente ≤ 0, y los clientes con saldo 0 y margen de $20 a $70 quedan en nivel Medio. ¿Se cambian los niveles de valor? → **A:** No; se mantienen y se documentan en el Glosario y en el Informe ejecutivo (US-013/BR-06).
- [x] **Q-09:** ¿Se escriben pruebas automatizadas? → **A:** No; verificación manual (TR-10, ADR-0006).
