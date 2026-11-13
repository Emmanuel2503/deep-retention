---
title: "Informe Ejecutivo de Proyecto: Sistema Deep Retention"
subtitle: "Retención selectiva de clientes con redes neuronales"
author: "Dirección de Estrategia y Rentabilidad de Clientes · Equipo de Desarrollo e Inteligencia de Negocios"
lang: es
fontsize: 10pt
mainfont: "Liberation Serif"
sansfont: "Liberation Sans"
monofont: "DejaVu Sans Mono"
geometry: "margin=2cm"
colorlinks: true
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
---

## 1. Resumen de Impacto Financiero y Retorno

Deep Retention estima, para cada cliente, la probabilidad de que abandone el banco y solo autoriza gasto de retención cuando la ganancia esperada de retenerlo supera el costo del beneficio ofrecido. Con los parámetros base del Simulador, el resultado sobre la cartera completa es el siguiente:

- Volumen Total de Clientes Analizados: 10,000
- Monto Total de Capital en Riesgo Crítico: $67,726,842.54
- Capital Rescatable Estimado: $42,417,857.08
- Inversión Total en Campañas de Fidelización: $308,950.00
- Retorno Sobre la Inversión (ROI): 178.7% (proyectado; > 0 por construcción)
- ROI Realizado con la Efectividad Supuesta (Clientes de Prueba): 180.4%

**Cómo leer estas cifras.**

- El **Capital en riesgo crítico** es el saldo total de los 761 clientes con probabilidad de fuga de 0.65 o más. En la cartera completa, el saldo ponderado por la probabilidad de fuga de cada cliente (Capital en riesgo) suma $180,038,107.29.
- El **Capital rescatable** es la parte de ese saldo que se espera conservar gracias a los incentivos: el saldo de cada cliente intervenido multiplicado por su probabilidad de fuga y por la efectividad del incentivo.
- La **Inversión** es la suma del costo de los 3,855 incentivos que el sistema recomienda. A cambio, el margen anual que se espera salvar es de $861,160.78, y las fugas evitadas esperadas son 347 clientes, el 25.6% de las fugas esperadas entre los clientes intervenidos.
- El **ROI proyectado es positivo por construcción**: el sistema solo asigna un incentivo cuando su ganancia neta esperada es mayor que cero, así que la suma no puede ser negativa. Por eso no se usa como prueba de rentabilidad.
- El **ROI realizado** es la prueba que sí podría fallar. Se calcula sobre los 601 clientes de prueba con incentivo, que la red nunca vio al entrenar, y usa su abandono real en lugar de la probabilidad estimada. Que sea positivo (180.4%) indica que la red acierta en los clientes donde se invierte. Sigue usando la efectividad supuesta de cada incentivo, no una efectividad observada: confirmarla es el objetivo de la prueba piloto de la sección 5.

**Supuestos financieros.** El dataset no incluye márgenes, así que se usa un margen anual estimado: `Margen = Saldo × 2% + Productos × $50 + Tiene tarjeta × $30 − $60 de costo de servicio`. El margen puede ser negativo (cliente deficitario). El costo del incentivo se paga una sola vez y se asume que la fuga ocurre dentro del mismo año que el margen. Todos estos valores, y el costo y la efectividad de cada incentivo, se pueden cambiar en el Simulador de parámetros de la aplicación.

| Incentivo | Costo | Efectividad supuesta |
|---|---:|---:|
| Gestor VIP y tarifa plana | $500.00 | 40% |
| Exoneración de comisiones | $150.00 | 30% |
| Bonificación transaccional | $50.00 | 20% |

## 2. Arquitectura de la Solución y Diagnóstico de Fuga

**Configuración de la Red Neuronal.** Perceptrón multicapa en Keras con dos capas ocultas: 64 neuronas ReLU con Batch Normalization y Dropout de 0.3, luego 32 neuronas ReLU con Dropout de 0.2, y una neurona de salida Sigmoide que entrega una probabilidad entre 0 y 1. Se entrena con el optimizador Adam (tasa de aprendizaje 0.001), lotes de 64 y ponderación de clases balanceada, porque solo el 20.4% de los clientes abandona. El entrenamiento se detiene cuando la pérdida de validación no mejora en 12 épocas y conserva los mejores pesos.

**Preparación de los datos.** Los 10,000 clientes se dividen de forma estratificada y con semilla fija en entrenamiento (70%), validación (15%) y prueba (15%). Las variables numéricas se estandarizan y País, Género y Tipo de tarjeta se codifican con One-Hot. Se excluyen los identificadores y la variable `Complain` (reclamo), que tiene una correlación de 0.996 con el abandono. En la práctica el reclamo se registra junto con la salida del cliente, así que usarla sería fuga de datos: el modelo parecería casi perfecto pero no serviría para anticipar el abandono.

**Calibración.** La ponderación de clases infla las probabilidades de la red, y la regla de decisión las usa directamente como montos esperados. Por eso la salida se calibra con el método de Platt sobre la partición de validación, y todas las decisiones usan la probabilidad calibrada.

Métricas de Diagnóstico Técnico: ROC-AUC: 0.88 | Precision-Recall AUC: 0.74 | Precisión de Calibración (Brier): 0.096

Las tres métricas se miden sobre los 1,500 clientes de prueba y superan los criterios de aceptación del proyecto: ROC-AUC de al menos 0.80, PR-AUC de al menos 0.55 y calibración que no empeore el Brier score. La calibración lo redujo de 0.143 a 0.096. Un PR-AUC de 0.74 es alto si se compara con el 0.20 que lograría un modelo al azar con esta proporción de abandono.

![Curva de fiabilidad: la probabilidad calibrada (naranja) sigue la diagonal de calibración perfecta mucho más de cerca que la salida sin calibrar (azul).](figures/reliability.png){width=55%}

**Factores Determinantes de Abandono.** Se obtienen con SHAP sobre la probabilidad calibrada, en una muestra de 500 clientes de prueba:

1. **Edad (`Age`).** Es el factor de mayor peso. El abandono sube con la edad: es del 8% hasta los 30 años, del 34% entre 41 y 50 y del 56% entre 51 y 60.
2. **Número de productos (`NumOfProducts`).** Los clientes con 2 productos casi no se van (8%), los que tienen uno solo abandonan un 28%, y con 3 o 4 productos el abandono pasa del 80%.
3. **Miembro activo (`IsActiveMember`).** Los clientes inactivos abandonan casi el doble que los activos (27% frente a 14%).

Les siguen el país (Alemania tiene un abandono del 32%, el doble que Francia y España) y el género.

![Contribución media absoluta de cada variable a la probabilidad de fuga (SHAP).](figures/shap_summary.png){width=60%}

**Limitación de SHAP con las variables one-hot.** Si SHAP se aplica directamente a las columnas one-hot, perturba cada columna por separado y la red termina evaluando clientes imposibles, por ejemplo de dos países a la vez o de ninguno. Para evitarlo, el explicador trabaja sobre las variables originales: cada variable categórica es un solo factor y sus columnas one-hot cambian juntas. Aun así, SHAP (KernelExplainer) supone que las variables son independientes, por lo que puede combinar valores poco realistas entre variables distintas. Además, sus contribuciones son una aproximación calculada con un fondo de 100 clientes de entrenamiento. Por eso los factores sirven para orientar la conversación con el cliente, no como causas demostradas del abandono.

## 3. Matriz de Decisión Comercial y Rentabilidad

La decisión de cada cliente sale de una sola fórmula, calculada para cada incentivo del catálogo:

`Ganancia Neta Esperada = Probabilidad de fuga × Efectividad del Incentivo × Margen del cliente − Costo del Incentivo`

El sistema asigna el incentivo con mayor ganancia, siempre que sea mayor que cero. Si ningún incentivo deja ganancia, no hay gasto de retención: la decisión es "Sin Acción Requerida" para los clientes estables y "Salida Permitida" para los demás. El segmento es una etiqueta descriptiva y no cambia la decisión.

| Segmento | Probabilidad Red | Valor Patrimonial | Clientes | Decisión del Sistema | Incentivo Asignado | Costo ($) | Margen Proyectado |
|---|---|---|---:|---|---|---:|---:|
| A: Alto Valor / Alto Riesgo | ≥ 0.65 | Superior | 444 | Retención Prioritaria (444) | Exoneración (436), Gestor VIP (8) | $69,400.00 | $231,080.83 |
| B: Medio / Riesgo Moderado | ≥ 0.65 | Medio | 286 | Retención (130), Salida Permitida (156) | Exoneración (110), Bonificación (20) | $17,500.00 | $32,892.00 |
| C: No Rentable | ≥ 0.65 | Bajo / Deficitario | 31 | Salida Permitida (31) | Sin intervención | $0.00 | Ahorro Operativo |
| D: Estable | < 0.30 | Cualquiera | 7,785 | Sin Acción Requerida (5,596), Retención (2,189) | Bonificación (2,180), Exoneración (9) | $110,350.00 | $89,996.11 |
| E: Riesgo Intermedio | 0.30 – 0.65 | Cualquiera | 1,454 | Retención (1,092), Salida Permitida (362) | Exoneración (571), Bonificación (521) | $111,700.00 | $198,242.10 |

*Margen Proyectado* es la suma de la ganancia neta esperada de los clientes con incentivo del segmento, es decir, el margen que se espera salvar menos el costo del incentivo. En total, el sistema recomienda 8 Gestores VIP, 1,126 Exoneraciones de comisiones y 2,721 Bonificaciones transaccionales, y deja sin gasto a 6,145 clientes (5,596 sin acción requerida y 549 salidas permitidas). El Segmento E no está en la plantilla del enunciado: reúne a los clientes de riesgo intermedio, entre 0.30 y 0.65.

**Tres diferencias con la plantilla del enunciado.** La regla de ganancia neta manda sobre la plantilla, y eso produce tres resultados que conviene explicar:

- **El Segmento D tiene inversión.** La plantilla asigna $0.00 a los clientes estables, pero un cliente de bajo riesgo con un margen alto también puede dejar ganancia, porque recibe incentivo cuando `Probabilidad de fuga > Costo / (Efectividad × Margen)`. De los 7,785 clientes estables, 2,189 cumplen esa condición: todos tienen un margen anual de al menos $880.58. Reciben sobre todo la Bonificación transaccional, que es barata. Su inversión es de $110,350.00 con una ganancia neta esperada de $89,996.11. Bloquearlos dejaría ese margen sin proteger.
- **El Gestor VIP es raro.** La asignación "según el perfil" no viene de reglas de elegibilidad sino de la fórmula. El Gestor VIP solo le gana a la Exoneración de comisiones si `Probabilidad de fuga × Margen > $3,500.00`, porque cuesta $350 más y solo agrega 10 puntos de efectividad. Esto lo limita a clientes de margen alto y riesgo muy alto: con los valores base son solo 8 clientes, todos con probabilidad de fuga de al menos 0.98 y margen de al menos $3,558.13. Para el resto del Segmento A, la Exoneración de comisiones deja más ganancia. Si el banco quiere más Gestores VIP, debe bajar su costo o confirmar en el piloto que su efectividad es mayor.
- **El Segmento C es pequeño.** Solo se considera "Bajo / Deficitario" a un cliente cuyo margen es de $0 o menos. Con el margen estimado, apenas 248 clientes de toda la cartera son deficitarios, y solo 31 de ellos tienen riesgo alto. El nivel "Medio" va desde un margen positivo hasta la mediana de los márgenes positivos ($2,005.62). Incluye 4,876 clientes, de los cuales 3,369 tienen saldo 0 y un margen de entre $20 y $170 (la mayoría, $70 o menos). Por eso 156 clientes del Segmento B quedan como Salida Permitida: su margen es de $240 o menos, tan bajo que ningún incentivo se paga, aunque su riesgo sea alto.

## 4. Operación de la Aplicación en Sucursales

**Procedimiento del Gestor de Cuentas.** El Ejecutivo de cuentas usa la pestaña "Buscador" de la aplicación cada vez que atiende a un cliente, en cinco pasos:

1. **Identificar al cliente.** Si ya es cliente del banco, lo busca por su identificador. Si es un cliente nuevo, ingresa sus datos en el formulario de la misma pestaña.
2. **Revisar el diagnóstico.** Lee la Probabilidad de fuga del cliente, la Decisión de retención sugerida y los Factores de fuga que explican ese riesgo, es decir, las variables que más lo suben o lo bajan.
3. **Ofrecer el Incentivo, si lo hay.** Cuando el sistema asigna un Incentivo (Gestor VIP y tarifa plana, Exoneración de comisiones o Bonificación transaccional), el Ejecutivo lo ofrece y usa los Factores de fuga para orientar la conversación: por ejemplo, si pesa la baja actividad, propone usos concretos de la cuenta; si pesa el número de productos, revisa con el cliente si los que tiene le sirven.
4. **Atender sin gasto cuando no corresponde retener.** Si la decisión es "Salida Permitida" o "Sin Acción Requerida", el Ejecutivo da la atención ordinaria de siempre y no ofrece ningún beneficio de retención. Así el presupuesto se reserva para los clientes en los que la retención deja ganancia neta.
5. **Registrar el resultado.** El Ejecutivo anota, fuera del sistema, si ofreció el Incentivo, si el cliente lo aceptó y si se quedó o se fue. Ese registro es la base para medir el resultado real de la prueba piloto.

La pestaña "Cartera" está pensada para la gerencia: muestra los indicadores consolidados y la matriz por segmento. La pestaña "Simulador" permite cambiar los costos y efectividades de los incentivos y los parámetros del margen, y ver al instante cómo cambian las decisiones y el ROI. Esos cambios duran solo la sesión y se pueden restablecer a los valores base.

**Mantenimiento del Modelo.** El mantenimiento es trimestral: cada trimestre se actualizan los datos de clientes y se reentrena la red neuronal. El reentrenamiento se adelanta si el ROC-AUC medido sobre clientes nuevos cae más de 0.05 respecto del valor reportado en este informe (0.88), porque esa caída indica que el comportamiento de los clientes cambió y el modelo dejó de reflejarlo. Cada reentrenamiento vuelve a calibrar la probabilidad y a calcular la Cartera puntuada, de modo que las cifras del Panel de cartera se renuevan con el modelo.

## 5. Conclusiones y Próximos Pasos

El sistema reemplaza la retención indiscriminada por una regla de rentabilidad: solo se gasta en un cliente cuando la ganancia esperada de retenerlo supera el costo del beneficio ofrecido. Con los valores base, deja sin gasto a 6,145 de los 10,000 clientes y concentra una inversión de $308,950.00 en 3,855 clientes. La red distingue bien a quienes se van (ROC-AUC 0.88), sus probabilidades son confiables después de calibrarlas, y el ROI realizado sobre clientes que no vio al entrenar es positivo. Antes de aplicarlo en toda la red de sucursales hay que comprobar que esa ganancia se confirma en la práctica, ya que la efectividad de cada Incentivo es hoy un supuesto y no una cifra observada.

**Prueba piloto.** Se propone un piloto de 3 meses en 2 o 3 sucursales:

- En cada sucursal piloto, los clientes con Incentivo asignado se reparten al azar en dos grupos. El grupo intervenido recibe el Incentivo que sugiere el sistema; el grupo de control no recibe Incentivos y sigue con la atención ordinaria.
- Al cierre de los 3 meses se comparan la tasa de fuga y el margen de ambos grupos. La diferencia entre ellos mide la efectividad real de cada Incentivo y permite calcular el ROI real del piloto con la inversión efectivamente gastada.
- Los registros del paso 5 del procedimiento de sucursal son la fuente de datos de esta comparación.

**Criterio de despliegue.** El despliegue general se aprueba solo si el ROI real del piloto es mayor que 0. Si lo es, se reemplazan las efectividades supuestas por las observadas en el Simulador de parámetros y se extiende la aplicación al resto de las sucursales. Si no lo es, se revisan los costos y las efectividades de los Incentivos antes de un nuevo piloto.

**Cronograma propuesto.**

| Etapa | Duración | Resultado |
|---|---|---|
| Preparación: elegir sucursales, capacitar a los Ejecutivos y definir el grupo de control | 2 a 4 semanas | Sucursales y grupos definidos |
| Prueba piloto con grupo de control | 3 meses | Registro de ofertas, aceptaciones y fugas |
| Evaluación del piloto | 2 semanas | ROI real y efectividades observadas |
| Despliegue general, si el ROI real es mayor que 0 | Por etapas, a partir del mes 5 | Aplicación en todas las sucursales |
