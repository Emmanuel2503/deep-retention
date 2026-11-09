---
id: VS-003
title: Evaluar con clientes de prueba y aceptar o rechazar el modelo
status: in-progress
story: US-003
covers: [AC-01, AC-02, AC-03]
adrs: []
depends_on: [VS-002]
---

# VS-003: Evaluar con clientes de prueba y aceptar o rechazar el modelo

## Goal
El Analista de datos ejecuta la evaluación desde el notebook de entrenamiento y obtiene ROC-AUC, PR-AUC, Brier antes y después de calibrar, la curva de fiabilidad y el veredicto de aceptación, calculados solo con los Clientes de prueba.

## Approach
`src/evaluate.py` lee la Cartera puntuada (con `pd.read_csv` de `models_dir`, no desde la app), filtra `split == "test"` y calcula las métricas con scikit-learn sobre `p_raw` y `p_churn`. `is_accepted` aplica US-003/BR-01, incluido el Brier (SRS/OBJ-02). `run_evaluation()` guarda `models/metrics.json` y la figura de fiabilidad (antes y después de calibrar) en `reports/figures/`. El notebook `02_train` llama a `run_evaluation()` después de `run_training()`. Si `accepted` es falso, no se versionan los artefactos y se repite el entrenamiento (US-003/AF-01); los turnos que dependen del modelo esperan.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `evaluate`, `is_accepted`, `run_evaluation` | `src/evaluate.py` |
| Notebook | Celda que llama a `run_evaluation()` y muestra el resultado | `notebooks/02_train.ipynb` |
| Artifacts | Métricas y figura de fiabilidad | `models/metrics.json`, `reports/figures/reliability.png` |

## Contracts
```
# src/evaluate.py
MIN_ROC_AUC = 0.80
MIN_PR_AUC = 0.55
Metrics = TypedDict{n_test: int, roc_auc: float, pr_auc: float,
                    brier_raw: float, brier_calibrated: float, accepted: bool}
evaluate(portfolio: DataFrame) -> Metrics            # solo filas split == "test"
is_accepted(roc_auc: float, pr_auc: float, brier_raw: float, brier_calibrated: float) -> bool
  # roc_auc >= MIN_ROC_AUC and pr_auc >= MIN_PR_AUC and brier_calibrated <= brier_raw
run_evaluation(models_dir=MODELS_DIR, reports_dir=REPORTS_DIR) -> Metrics
  # escribe models_dir/metrics.json y reports_dir/figures/reliability.png
```

## Tasks
- [x] **T-01:** Implementar `evaluate` sobre los Clientes de prueba → AC-01, AC-02
- [x] **T-02:** Implementar `is_accepted` → AC-03
- [x] **T-03:** Implementar `run_evaluation` con `metrics.json` y la curva de fiabilidad → AC-02
- [ ] **T-04:** Agregar la celda de evaluación al notebook y versionar los artefactos → AC-01

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | `metrics.json` tiene `n_test` = 1,500; en una celda temporal, invertir `p_churn` de las filas que no son de prueba y volver a llamar a `evaluate()` da el mismo ROC-AUC | manual | `notebooks/02_train.ipynb` |
| AC-02 | `metrics.json` contiene `brier_raw` y `brier_calibrated`, y `reports/figures/reliability.png` muestra las dos curvas | manual | `notebooks/02_train.ipynb` |
| AC-03 | En una celda: `is_accepted(0.78, 0.70, 0.12, 0.10)` y `is_accepted(0.85, 0.60, 0.12, 0.15)` son falsos; `is_accepted(0.85, 0.60, 0.15, 0.12)` es verdadero | manual | `notebooks/02_train.ipynb` |

## Out of scope
- Factores de fuga → VS-004.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Gabriel (turno 1)
