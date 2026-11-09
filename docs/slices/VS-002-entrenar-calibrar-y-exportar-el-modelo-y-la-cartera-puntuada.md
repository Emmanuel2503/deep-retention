---
id: VS-002
title: Entrenar, calibrar y exportar el modelo y la cartera puntuada
status: ready
story: US-002
covers: [AC-01, AC-02, AC-03]
adrs: [ADR-0002]
depends_on: [VS-001]
---

# VS-002: Entrenar, calibrar y exportar el modelo y la cartera puntuada

## Goal
El Analista de datos ejecuta el notebook de entrenamiento en Colab (o `python -m src.train`) y obtiene en `models/` todo lo necesario para estimar la Probabilidad de fuga sin reentrenar, incluida la Cartera puntuada que usa la aplicación.

## Approach
`run_training()` en `src/train.py` encadena: `keras.utils.set_random_seed(seed)` → carga y variables de entrada (VS-001) → partición estratificada 70/15/15 con semilla fija → preprocesador (StandardScaler para las numéricas y OneHotEncoder para las categóricas) ajustado solo con el entrenamiento → MLP de SRS/TR-01 con optimizador Adam (lr 1e-3), lotes de 64, `class_weight` balanceado y EarlyStopping sobre `val_loss` con paciencia 12 y `restore_best_weights` → calibración Platt (regresión logística sobre el logit de la salida) ajustada con la validación → exporta los artefactos y la Cartera puntuada con las columnas de ADR-0002. `src/inference.py` ofrece `ChurnPredictor` para cargar los artefactos y predecir; `load_portfolio()` lo implementa VS-005. El notebook `02_train` clona el repositorio y llama a `run_training()` (ADR-0001). Al terminar, se fijan en `requirements.txt` con `==` las versiones de Colab de tensorflow, scikit-learn, joblib, numpy y pandas (SRS/TR-02).

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `split_data`, `build_preprocessor` | `src/preprocessing.py` |
| Domain | `build_model`, `train_model`, `fit_calibrator` | `src/model.py` |
| Domain | `run_training` y punto de entrada `__main__` | `src/train.py` |
| Inference | `ChurnPredictor` | `src/inference.py` |
| Notebook | Clona el repositorio, instala dependencias, llama a `run_training()` e imprime la versión de Python y las de las librerías | `notebooks/02_train.ipynb` |
| Infrastructure | Versiones exactas de Colab | `requirements.txt` |
| Artifacts | Modelo, preprocesador, calibrador, variables y Cartera puntuada | `models/` |

## Contracts
```
# src/preprocessing.py
split_data(df, seed: int = SEED) -> tuple[DataFrame, DataFrame, DataFrame]   # train, val, test; 70/15/15 estratificado por Exited
build_preprocessor(features: list[str]) -> ColumnTransformer
  # numéricas: StandardScaler; CATEGORICAL: OneHotEncoder(handle_unknown="ignore")

# src/model.py
PATIENCE = 12
build_model(n_inputs: int) -> keras.Model
  # Dense(64, relu) → BatchNorm → Dropout(0.3) → Dense(32, relu) → Dropout(0.2) → Dense(1, sigmoid)
  # Adam(1e-3), binary_crossentropy
train_model(model, X_tr, y_tr, X_val, y_val, *, epochs=200, patience=PATIENCE, batch_size=64)
  -> TrainOutcome{history: keras.callbacks.History, stopped_epoch: int, best_epoch: int}
fit_calibrator(p_raw_val: ndarray, y_val: ndarray) -> sklearn LogisticRegression

# src/train.py
run_training(data_path=DATA_PATH, out_dir=MODELS_DIR, seed=SEED)
  -> TrainingResult{split_ids: dict["train"|"val"|"test", list[int]], stopped_epoch: int, best_epoch: int}
  # primera instrucción: keras.utils.set_random_seed(seed)

# artefactos en out_dir
model.keras
preprocessor.joblib
calibrator.joblib
features.json           { "features": [str], "excluded": [ExcludedFeature],
                          "categories": { "Geography": [str], "Gender": [str], "Card Type": [str] } }
portfolio_scored.csv    columnas de ADR-0002 (split, p_raw, p_churn)

# src/inference.py
class ChurnPredictor:
    @classmethod load(models_dir: Path = MODELS_DIR) -> ChurnPredictor
    features: list[str]; categories: dict[str, list[str]]
    transform(df) -> ndarray                 # preprocesador
    predict_raw(df) -> ndarray[float]        # salida de la red, [0, 1]
    predict(df) -> ndarray[float]            # Probabilidad de fuga calibrada, [0, 1]
    predict_transformed(X: ndarray) -> ndarray[float]   # calibrador ∘ red sobre filas ya transformadas (para SHAP)
```

## Tasks
- [ ] **T-01:** Implementar `split_data` → AC-01
- [ ] **T-02:** Implementar `build_preprocessor`, `build_model` → AC-03
- [ ] **T-03:** Implementar `train_model` con `class_weight` y EarlyStopping → AC-02
- [ ] **T-04:** Implementar `fit_calibrator` → AC-03
- [ ] **T-05:** Implementar `run_training` con la semilla de Keras y la exportación de artefactos y de la Cartera puntuada → AC-03
- [ ] **T-06:** Implementar `ChurnPredictor` → AC-03
- [ ] **T-07:** Crear `notebooks/02_train.ipynb`, entrenar en Colab, comprobar que Colab usa Python 3.12 (si no, avisar al equipo antes de seguir), fijar en `requirements.txt` las versiones impresas y versionar `models/` → AC-03

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Dos llamadas a `split_data(load_dataset())` en el notebook devuelven los mismos `CustomerId` por partición (comparar conjuntos), con 7,000/1,500/1,500 clientes y abandono 0.204 ± 0.005 en cada una | manual | `notebooks/02_train.ipynb` |
| AC-02 | `PATIENCE` está entre 10 y 15; en el resultado del entrenamiento, `stopped_epoch − best_epoch` = `PATIENCE`, y `model.evaluate` sobre la validación da la `val_loss` de `best_epoch` del historial | manual | `notebooks/02_train.ipynb` |
| AC-03 | En el `venv/` local con Python 3.12, creado con pip o con uv (no en Colab), tras `pip install -r requirements.txt`: `ChurnPredictor.load()` predice para los 10,000 clientes valores en [0, 1] sin errores ni avisos de versión; `models/portfolio_scored.csv` tiene 10,000 filas, las columnas de ADR-0002 y `p_churn` en [0, 1] | manual | terminal local (`venv/bin/python`) |

## Out of scope
- Métricas sobre los Clientes de prueba → VS-003.
- `load_portfolio()` y `config.portfolio_path()` → VS-005.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Gabriel (turno 1)
