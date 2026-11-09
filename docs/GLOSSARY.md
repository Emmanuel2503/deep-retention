---
title: Glossary
updated: 2026-11-08
---

# Glossary

## Terms

### Analista de datos
Miembro del equipo que explora los datos, entrena y evalúa la red y redacta el Informe ejecutivo.
- **Avoid:** data scientist, desarrollador
- **Related:** Informe ejecutivo

### Buscador por cliente
Vista de la aplicación donde el Ejecutivo de cuentas consulta a un cliente y obtiene su Probabilidad de fuga, su Ganancia neta esperada y su Decisión de retención.
- **Avoid:** consulta individual, ficha de cliente
- **Related:** Ejecutivo de cuentas, Decisión de retención

### Capital en riesgo
Saldo de la Cartera que se espera perder por fuga: la suma de `Balance × Probabilidad de fuga` de todos los clientes.
- **Avoid:** balance en riesgo, saldo en riesgo
- **Related:** Capital rescatable, Cartera

### Capital en riesgo crítico
Saldo total de los clientes de la Cartera con Probabilidad de fuga ≥ 0.65: la suma de su `Balance`, sin ponderar por la probabilidad.
- **Avoid:** saldo crítico
- **Related:** Capital en riesgo, Segmento

### Capital rescatable
Parte del Capital en riesgo que se espera conservar gracias a los Incentivos asignados: la suma de `Balance × Probabilidad de fuga × Efectividad` de los clientes con Incentivo.
- **Avoid:** dinero a rescatar, balance salvado
- **Related:** Capital en riesgo, Margen salvado

### Cartera
Conjunto de clientes analizados por el sistema. Por defecto son los 10,000 clientes del dataset.
- **Avoid:** portafolio, base de clientes
- **Related:** Cliente de prueba, Panel de cartera

### Cartera puntuada
Archivo `models/portfolio_scored.csv` con los datos de cada cliente de la Cartera, su partición y su Probabilidad de fuga ya calculada por la red. La aplicación la lee en lugar de ejecutar la red sobre toda la Cartera.
- **Avoid:** scores, predicciones
- **Related:** Cartera, Probabilidad de fuga

### Cliente de prueba
Cliente de la partición de prueba (15% de la Cartera), que la red no vio durante el entrenamiento ni la calibración.
- **Avoid:** test set, holdout
- **Related:** Cartera

### Comisión por producto
Ingreso anual del banco por cada producto contratado por el cliente; parámetro del Margen del cliente. Valor base: $50.
- **Related:** Margen del cliente, Simulador de parámetros

### Comisión por tarjeta
Ingreso anual del banco si el cliente tiene tarjeta de crédito; parámetro del Margen del cliente. Valor base: $30.
- **Related:** Margen del cliente, Simulador de parámetros

### Costo de servicio
Costo anual fijo de atender a un cliente; se resta en el Margen del cliente. Valor base: $60.
- **Related:** Margen del cliente, Simulador de parámetros

### Costo del Incentivo
Gasto unitario del banco por aplicar un Incentivo a un cliente.
- **Avoid:** precio, costo de campaña
- **Related:** Incentivo, Inversión en retención

### Decisión de retención
Resultado del sistema para un cliente: el Incentivo asignado, Salida Permitida o Sin Acción Requerida.
- **Avoid:** recomendación, acción comercial
- **Related:** Incentivo, Salida Permitida, Ganancia neta esperada

### Efectividad
Probabilidad de que un Incentivo evite la fuga de un cliente que se iba a ir.
- **Avoid:** tasa de éxito, conversión
- **Related:** Incentivo
- **Example:** La Bonificación transaccional tiene Efectividad base del 20%.

### Ejecutivo de cuentas
Gestor de sucursal que consulta a un cliente en el Buscador por cliente y aplica la Decisión de retención.
- **Avoid:** gestor, asesor, ejecutivo
- **Related:** Buscador por cliente

### Factor de fuga
Variable del cliente que más contribuye a la Probabilidad de fuga estimada por la red, según el análisis de explicabilidad.
- **Avoid:** driver, causa
- **Related:** Probabilidad de fuga
- **Example:** Edad, Número de productos.

### Fugas evitadas esperadas
Número esperado de clientes que dejan de fugarse gracias a los Incentivos asignados: la suma de `Probabilidad de fuga × Efectividad` de los clientes con Incentivo. Es la efectividad proyectada de las intervenciones.
- **Avoid:** efectividad proyectada (como nombre del indicador), clientes retenidos
- **Related:** Efectividad, Panel de cartera

### Ganancia neta esperada
Beneficio esperado de aplicar un Incentivo a un cliente: `Probabilidad de fuga × Efectividad × Margen del cliente − Costo del Incentivo`.
- **Avoid:** GNE en documentos, beneficio, valor esperado
- **Related:** Decisión de retención, Margen del cliente
- **Example:** Probabilidad de fuga 0.80, Margen del cliente $2,070, Exoneración de comisiones: 0.80 × 0.30 × 2,070 − 150 = $346.80.

### Incentivo
Acción de retención del catálogo, con un Costo del Incentivo y una Efectividad: Gestor VIP y tarifa plana, Exoneración de comisiones o Bonificación transaccional.
- **Avoid:** promoción, beneficio, campaña
- **Related:** Costo del Incentivo, Efectividad, Decisión de retención

### Informe ejecutivo
Documento PDF dirigido a la Dirección de Estrategia que resume el impacto financiero, la arquitectura de la red, la matriz de segmentos, la operación y los próximos pasos.
- **Avoid:** reporte, informe técnico
- **Related:** Dirección de Estrategia

### Inversión en retención
Suma de los Costos del Incentivo de todos los Incentivos asignados en la Cartera.
- **Avoid:** gasto total, presupuesto
- **Related:** Costo del Incentivo, ROI

### Margen del cliente
Ganancia anual que el cliente genera al banco, estimada a partir de su saldo, sus productos y su tarjeta, menos el costo de servicio. Puede ser negativa.
- **Avoid:** valor del cliente, rentabilidad, CLV
- **Related:** Ganancia neta esperada, Segmento
- **Example:** Balance $100,000, 2 productos, con tarjeta: 2,000 + 100 + 30 − 60 = $2,070.

### Margen salvado
Margen del cliente que se espera conservar gracias a los Incentivos asignados: la suma de `Probabilidad de fuga × Efectividad × Margen del cliente` de los clientes con Incentivo.
- **Related:** ROI, Capital rescatable

### Nivel de valor
Clasificación del Margen del cliente usada en el Segmento: Bajo/Deficitario si es ≤ 0; Medio si es positivo y no supera la mediana de los márgenes positivos de la Cartera; Superior si la supera. "Medio" no significa saldo medio: un cliente con saldo 0 y dos productos (margen $40) es Medio. Con los Valores base, muy pocos clientes son Bajo/Deficitario; la cifra exacta sale de la matriz de segmentos.
- **Avoid:** categoría de cliente
- **Related:** Margen del cliente, Segmento

### Panel de cartera
Vista de la aplicación con los indicadores consolidados de la Cartera y la matriz de segmentos.
- **Avoid:** dashboard
- **Related:** Cartera, Segmento

### Probabilidad de fuga
Probabilidad calibrada, entre 0 y 1, de que un cliente abandone el banco, estimada por la red.
- **Avoid:** score, churn, riesgo (como número)
- **Related:** Ganancia neta esperada, Factor de fuga

### ROI
Retorno proyectado de la Inversión en retención: `(Margen salvado − Inversión en retención) / Inversión en retención`. Es > 0 por construcción siempre que haya inversión, porque solo se asignan Incentivos con Ganancia neta esperada > 0.
- **Related:** Inversión en retención, Margen salvado, ROI realizado

### ROI realizado
Retorno de la Inversión en retención sobre los Clientes de prueba usando el abandono real (`Exited`) en lugar de la Probabilidad de fuga: `(Σ Exited × Efectividad × Margen del cliente − Σ Costo del Incentivo) / Σ Costo del Incentivo` de los Clientes de prueba con Incentivo. Puede ser negativo. La Efectividad sigue siendo la supuesta, así que no es un retorno observado; en el Informe ejecutivo se presenta como "ROI realizado con la Efectividad supuesta".
- **Avoid:** ROI real, backtest (como nombre del indicador)
- **Related:** ROI, Cliente de prueba

### Salida Permitida
Decisión de retención de un cliente fuera del Segmento D para el que ningún Incentivo tiene Ganancia neta esperada > 0: no se gasta en retenerlo.
- **Avoid:** sin intervención, dejar ir
- **Related:** Decisión de retención, Sin Acción Requerida

### Segmento
Etiqueta descriptiva (A a E) de un cliente según su Probabilidad de fuga y su nivel de valor; no cambia la Decisión de retención.
- **Avoid:** grupo, cluster
- **Related:** Margen del cliente, Panel de cartera

### Sin Acción Requerida
Decisión de retención de un cliente del Segmento D (Probabilidad de fuga < 0.30) para el que ningún Incentivo tiene Ganancia neta esperada > 0: recibe atención ordinaria, sin gasto de retención.
- **Avoid:** mantenimiento ordinario, estable (como decisión)
- **Related:** Decisión de retención, Salida Permitida, Segmento

### Simulador de parámetros
Vista de la aplicación donde la Dirección de Estrategia ajusta costos, Efectividad y parámetros del Margen del cliente y ve su impacto en la Cartera.
- **Avoid:** simulador de campañas
- **Related:** Panel de cartera

### Spread
Porcentaje anual del Balance que el banco gana con el saldo del cliente; parámetro del Margen del cliente. Valor base: 2%.
- **Avoid:** tasa, margen financiero
- **Related:** Margen del cliente, Simulador de parámetros

### Valores base
Valores iniciales de los parámetros del Simulador de parámetros (SRS/BR-03 y SRS/BR-04). Se usan al abrir la aplicación, al restablecer y en el Informe ejecutivo.
- **Avoid:** valores por defecto, parámetros iniciales
- **Related:** Simulador de parámetros

### Volumen de clientes analizados
Número de clientes sobre los que se calculan los indicadores del Panel de cartera: 10,000 con la Cartera completa o 1,500 con solo los Clientes de prueba.
- **Related:** Cartera, Panel de cartera
