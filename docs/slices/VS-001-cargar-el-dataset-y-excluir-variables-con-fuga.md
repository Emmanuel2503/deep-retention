---
id: VS-001
title: Cargar el dataset y excluir variables con fuga
status: ready
story: US-001
covers: [AC-01, AC-02, AC-03]
adrs: []
depends_on: []
---

# VS-001: Cargar el dataset y excluir variables con fuga

## Goal
El Analista de datos abre el notebook de exploración en Colab, ve el volumen de clientes, la tasa de abandono y la correlación de cada variable con `Exited`, y obtiene la lista de variables excluidas con su motivo.

## Approach
Se crea la estructura base del repositorio (`src/`, `data/`, `notebooks/`, `requirements.txt`) y se mueve el dataset a `data/`. `src/preprocessing.py` carga el dataset, resume su volumen y abandono, y detecta las variables con fuga por correlación con `Exited`: las variables numéricas directamente, y las categóricas por el máximo valor absoluto de la correlación de sus columnas one-hot. `excluded_features()` une los identificadores, `Complain` y cualquier otra variable detectada. El notebook `01_eda` solo llama a estas funciones y grafica las distribuciones (ADR-0001). Es el tracer bullet del pipeline de datos. Como este slice no depende del modelo, al terminarlo pueden empezar VS-002 y VS-005 en paralelo.

## Changes
| Layer | Change | Location |
|---|---|---|
| Data | Mover el dataset desde `docs/dataset-prediction/` | `data/Customer-Churn-Records.csv` |
| Config | Rutas del repositorio y semilla | `src/config.py` |
| Domain | Carga, resumen y detección de variables con fuga | `src/preprocessing.py` |
| Notebook | Exploración que llama a `src/` y grafica | `notebooks/01_eda.ipynb` |
| Infrastructure | Dependencias (pandas, numpy, scikit-learn, tensorflow, shap, streamlit, matplotlib, joblib); VS-002 fija sus versiones exactas | `requirements.txt` |

## Contracts
```
# src/config.py
REPO_ROOT: Path
DATA_PATH   = REPO_ROOT / "data" / "Customer-Churn-Records.csv"
MODELS_DIR  = REPO_ROOT / "models"
REPORTS_DIR = REPO_ROOT / "reports"
SEED = 42

# src/preprocessing.py
TARGET = "Exited"
ID_COLUMNS = ["RowNumber", "CustomerId", "Surname"]
KNOWN_LEAKY = ["Complain"]
CATEGORICAL = ["Geography", "Gender", "Card Type"]
LEAK_THRESHOLD = 0.5

ExcludedFeature = TypedDict{feature: str, reason: str, correlation: float | None}
  reason ∈ {"identificador", "fuga de datos"}

load_dataset(path: Path = DATA_PATH) -> pd.DataFrame
dataset_summary(df) -> {"n_customers": int, "churn_rate": float}
feature_correlations(df) -> dict[str, float]          # |corr| con TARGET, por variable original
find_leaky_features(df, threshold: float = LEAK_THRESHOLD) -> list[ExcludedFeature]
excluded_features(df) -> list[ExcludedFeature]        # ID_COLUMNS + KNOWN_LEAKY + detectadas, sin duplicados
input_features(df) -> list[str]                       # columnas - TARGET - excluidas
```

## Tasks
- [ ] **T-01:** Crear `src/config.py`, `requirements.txt` y mover el dataset a `data/` → none
- [ ] **T-02:** Implementar `load_dataset` y `dataset_summary` → AC-01
- [ ] **T-03:** Implementar `feature_correlations`, `find_leaky_features` y `excluded_features` → AC-02, AC-03
- [ ] **T-04:** Crear `notebooks/01_eda.ipynb` que llame a las funciones y grafique distribuciones y correlaciones → AC-01, AC-02

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | El notebook muestra 10,000 clientes y tasa de abandono 0.204 (± 0.001) | manual | `notebooks/01_eda.ipynb` |
| AC-02 | La tabla de excluidas del notebook contiene `RowNumber`, `CustomerId`, `Surname` ("identificador") y `Complain` ("fuga de datos", correlación 0.996 ± 0.001); `Satisfaction Score`, `Card Type` y `Point Earned` aparecen en `input_features` | manual | `notebooks/01_eda.ipynb` |
| AC-03 | En una celda temporal, agregar a una copia del dataset una columna igual a `Exited` con 10% de valores invertidos (correlación ≈ 0.73) y llamar a `excluded_features`: la columna aparece con motivo "fuga de datos". Borrar la celda después | manual | `notebooks/01_eda.ipynb` |

## Out of scope
- Particiones y preprocesador para entrenar → VS-002.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Gabriel (turno 1)
