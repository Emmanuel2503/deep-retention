# Deep Retention

Sistema de retención selectiva de clientes bancarios. Una red neuronal (MLP) estima la probabilidad de fuga de cada cliente y una regla financiera decide si conviene o no invertir en retenerlo.

📄 **[Informe ejecutivo (PDF)](reports/informe_ejecutivo.pdf)** · 📐 **[Especificación (SRS)](docs/SRS.md)** · 📖 **[Glosario](docs/GLOSSARY.md)**

## Problema

Retener a todos los clientes por igual reduce el margen del banco. El sistema solo autoriza una acción de retención si la ganancia neta esperada es positiva:

```
Ganancia Neta Esperada = (P_fuga × Efectividad × Margen) − Costo_incentivo
```

- Se calcula la ganancia de cada incentivo y se recomienda el de **mayor ganancia**, si es mayor que cero.
- Si ningún incentivo es rentable, el cliente queda como **Salida Permitida**, o como **Sin Acción Requerida** si su riesgo es bajo (P_fuga < 0.30).
- `P_fuga` es la probabilidad **calibrada** de la red. Nunca se usa un umbral fijo como 0.5.

## Dataset

[Bank Customer Churn (Kaggle)](https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn): 10,000 clientes, 20.4% de abandono. Archivo: `data/Customer-Churn-Records.csv`.

- **Excluidas:** `RowNumber`, `CustomerId`, `Surname` (identificadores) y `Complain` (fuga de datos: correlación de 0.996 con `Exited`). También se excluye cualquier otra variable con correlación > 0.5 con `Exited` detectada en el EDA.
- **Estandarizadas (StandardScaler):** `CreditScore`, `Age`, `Tenure`, `Balance`, `NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`, `Satisfaction Score`, `Point Earned`.
- **One-Hot:** `Geography`, `Gender`, `Card Type`.
- **Particiones:** 70% entrenamiento, 15% validación y 15% prueba, estratificadas y con semilla fija.

## Modelo

- **Framework:** Keras (TensorFlow).
- **Arquitectura:** Dense 64 ReLU + BatchNorm + Dropout 0.3 → Dense 32 ReLU + Dropout 0.2 → Dense 1 Sigmoide.
- **Entrenamiento:** Adam (lr 1e-3), lotes de 64, `class_weight` balanceado y Early Stopping sobre `val_loss` con paciencia 12 y restauración de los mejores pesos.
- **Calibración:** Platt sobre la partición de validación, porque `class_weight` infla las probabilidades.
- **Explicabilidad:** SHAP sobre la probabilidad calibrada: global (factores de fuga) y por cliente en la aplicación.

Métricas sobre los clientes de prueba. El modelo se acepta solo si ROC-AUC ≥ 0.80, PR-AUC ≥ 0.55 y la calibración no empeora el Brier score.

| Métrica | Valor |
|---|---|
| ROC-AUC | _pendiente_ |
| PR-AUC | _pendiente_ |
| Brier (sin calibrar → calibrado) | _pendiente_ |

## Supuestos financieros

No hay datos de margen en el dataset, así que se estima un **margen anual proxy**. Todos los valores se pueden ajustar en el Simulador:

```
Margen = Balance × 2% + NumOfProducts × $50 + HasCrCard × $30 − $60 (costo de servicio)
```

| Incentivo | Costo | Efectividad |
|---|---|---|
| Gestor VIP y tarifa plana | $500 | 40% |
| Exoneración de comisiones | $150 | 30% |
| Bonificación transaccional | $50 | 20% |

**Segmentos.** Son solo descriptivos: la decisión la toma siempre la fórmula. El nivel de valor depende del margen: Bajo/Deficitario si es ≤ 0; Medio o Superior según la mediana de los márgenes positivos ("Medio" incluye clientes con saldo 0 y margen positivo pequeño). Un cliente de cualquier segmento, incluido D, recibe incentivo si su ganancia neta esperada es positiva.

| Segmento | P_fuga | Nivel de valor |
|---|---|---|
| A: Alto valor / Alto riesgo | ≥ 0.65 | Superior |
| B: Medio / Riesgo moderado | ≥ 0.65 | Medio |
| C: No rentable | ≥ 0.65 | Bajo/Deficitario |
| D: Estable | < 0.30 | Cualquiera |
| E: Riesgo intermedio | 0.30 – 0.65 | Cualquiera |

## Aplicación

Una sola app Streamlit con tres pestañas:

- **Buscador:** consulta por `CustomerId` o con un formulario para clientes nuevos, con validación de límites de negocio. Muestra la probabilidad de fuga, el margen, la ganancia neta esperada de cada incentivo, el segmento, la decisión y la explicación SHAP.
- **Cartera:** clientes analizados, capital en riesgo, capital en riesgo crítico, capital rescatable, inversión, margen salvado, ROI, fugas evitadas esperadas y la matriz por segmento. Incluye un filtro para ver solo los clientes de prueba, con el ROI realizado según el abandono real.
- **Simulador:** costo y efectividad de cada incentivo y parámetros del margen. Los cambios se aplican a las tres pestañas, duran solo la sesión y se pueden restablecer a los valores base.

## Estructura del repositorio

```
deep-retention/
├── app/
│   └── app.py              # Streamlit: Buscador, Cartera, Simulador
├── data/                   # dataset
│   └── fixtures/           # carteras puntuadas de ejemplo para verificar la app
├── docs/                   # SRS, glosario, épicas, historias, ADRs y slices
├── models/                 # modelo, preprocesador, calibrador, métricas y cartera puntuada
├── notebooks/
│   ├── 01_eda.ipynb        # exploración y detección de fuga de datos
│   └── 02_train.ipynb      # entrenamiento, evaluación y SHAP (Google Colab)
├── reports/
│   ├── figures/
│   ├── informe.md
│   └── informe_ejecutivo.pdf
├── src/                    # toda la lógica
│   ├── config.py           # rutas y semilla
│   ├── preprocessing.py    # carga, variables excluidas, particiones, preprocesador
│   ├── model.py            # MLP, entrenamiento, calibración
│   ├── train.py            # flujo completo de entrenamiento y exportación
│   ├── evaluate.py         # métricas sobre clientes de prueba
│   ├── explain.py          # SHAP global y por cliente
│   ├── inference.py        # predicción y carga de la cartera puntuada
│   ├── finance.py          # reglas financieras
│   ├── validation.py       # validación de entradas
│   └── report.py           # cifras del informe
├── requirements.txt
└── README.md
```

Reglas de arquitectura ([ADRs](docs/adrs/)):
- **ADR-0001:** toda la lógica vive en `src/`; notebooks, script y app solo la llaman.
- **ADR-0002:** la app lee la cartera puntuada (`models/portfolio_scored.csv`) y solo usa la red para clientes nuevos y explicaciones.
- **ADR-0007** (reemplaza a ADR-0003): los parámetros del simulador viven en la sesión, cambian solo en callbacks y se pasan explícitamente a las reglas financieras.
- **ADR-0005:** los type hints son opcionales y no se usa verificador de tipos.
- **ADR-0006:** no hay pruebas automatizadas; la verificación es manual.

## Instalación y uso

### Requisitos

- **Python 3.12**, la misma versión que usa Google Colab. TensorFlow no tiene paquetes para Python 3.14, y las versiones fijadas en `requirements.txt` son las de Colab.
- El entorno virtual se llama **`venv/`**, en la raíz del repositorio (no `.venv/`).
- Para el informe en PDF: pandoc y xelatex.

Elige una de las dos opciones de instalación.

### Opción A: pip

Requiere Python 3.12 instalado en el sistema (Fedora: `sudo dnf install python3.12`).

```bash
git clone https://github.com/Emmanuel2503/deep-retention.git
cd deep-retention
python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Opción B: uv

[uv](https://docs.astral.sh/uv/) instala Python 3.12 sin tocar el Python del sistema. Si `uv venv` responde "No interpreter found for Python 3.12", instálalo primero con `uv python install 3.12`.

```bash
git clone https://github.com/Emmanuel2503/deep-retention.git
cd deep-retention
uv venv --python 3.12 --seed venv   # --seed instala pip dentro de venv/
source venv/bin/activate            # Windows: venv\Scripts\activate
uv pip install -r requirements.txt
```

Las dependencias viven solo en `requirements.txt`: no uses `uv add`, `uv sync` ni `uv lock`, que crean `pyproject.toml` y `uv.lock`. Para agregar una dependencia, escríbela en `requirements.txt` y vuelve a ejecutar `uv pip install -r requirements.txt`.

### Uso

Todos los comandos se ejecutan con el entorno activado (`source venv/bin/activate`), igual con pip o con uv. Sin activarlo, usa las rutas `venv/bin/python` y `venv/bin/streamlit`.

Entrenar el modelo es opcional: el repositorio ya incluye los artefactos en `models/`. El entrenamiento se ejecuta en **Google Colab** con `notebooks/02_train.ipynb`, que clona el repositorio, entrena, evalúa y genera los artefactos de `models/`. El equivalente en script es:

```bash
python -m src.train
```

Lanzar la aplicación:

```bash
streamlit run app/app.py
```

Verificación manual con una cartera de ejemplo (probabilidades fijas, ver la tabla Tests de cada slice):

```bash
DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv streamlit run app/app.py
```

Generar el informe en PDF:

```bash
python -m src.report            # imprime las cifras del informe
pandoc reports/informe.md -o reports/informe_ejecutivo.pdf --pdf-engine=xelatex --resource-path=reports
```

### Despliegue en Streamlit Community Cloud

Al crear la app, elige **Python 3.12** en "Advanced settings". Streamlit Cloud instala `requirements.txt` por su cuenta y ejecuta `app/app.py`.
