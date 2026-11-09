---
id: VS-004
title: Calcular los factores de fuga globales
status: ready
story: US-004
covers: [AC-01]
adrs: []
depends_on: [VS-002]
---

# VS-004: Calcular los factores de fuga globales

## Goal
El Analista de datos obtiene desde el notebook la figura resumen SHAP y la lista ordenada de Factores de fuga, con una entrada por variable original, lista para el Informe ejecutivo.

## Approach
`src/explain.py` construye un `shap.KernelExplainer` en el espacio transformado por el preprocesador, sobre `predictor.predict_transformed` (la red seguida del calibrador), así que explica la Probabilidad de fuga calibrada (SRS/TR-06, SRS/BR-07). El fondo lo elige `background_sample`: 100 clientes de `split == "train"` de la Cartera puntuada, con la semilla fija, o todos si hay menos. Se aplica a 500 Clientes de prueba (misma semilla), se suman las contribuciones de las columnas one-hot de cada variable categórica para volver a la variable original y se ordena por la media del valor absoluto. Guarda la figura y la lista. VS-009 reutiliza `background_sample` y `build_explainer` por cliente. Con KernelExplainer, el cálculo de 500 clientes tarda varios minutos en Colab.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `background_sample`, `build_explainer`, `original_feature`, `global_factors`, `run_global_explanation` | `src/explain.py` |
| Notebook | Celda que llama a `run_global_explanation()` | `notebooks/02_train.ipynb` |
| Artifacts | Figura resumen y lista de factores | `reports/figures/shap_summary.png`, `models/global_factors.json` |

## Contracts
```
# src/explain.py
BACKGROUND_SIZE = 100
GLOBAL_SAMPLE_SIZE = 500
background_sample(portfolio: DataFrame, n: int = BACKGROUND_SIZE, seed: int = SEED) -> DataFrame
  # filas split == "train"; muestra de n con la semilla, o todas si hay menos de n
build_explainer(predictor: ChurnPredictor, background: DataFrame) -> Explainer
  # KernelExplainer(predictor.predict_transformed, predictor.transform(background))
original_feature(column: str, features: list[str]) -> str     # "cat__Geography_France" → "Geography"
global_factors(explainer, sample: DataFrame) -> list[{"feature": str, "mean_abs_contribution": float}]
  # una entrada por variable original, orden descendente
run_global_explanation(models_dir=MODELS_DIR, reports_dir=REPORTS_DIR,
                       sample_size=GLOBAL_SAMPLE_SIZE) -> list[...]
  # escribe models_dir/global_factors.json y reports_dir/figures/shap_summary.png
```

## Tasks
- [ ] **T-01:** Implementar `background_sample`, `build_explainer` y `original_feature` → AC-01
- [ ] **T-02:** Implementar `global_factors` con agregación por variable original → AC-01
- [ ] **T-03:** Implementar `run_global_explanation` y la figura; ejecutarla en Colab y versionar los artefactos → AC-01

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Tras `run_global_explanation()` en Colab: existe `shap_summary.png`, y `global_factors.json` tiene cada variable de `features.json["features"]` una sola vez, ordenadas de mayor a menor `mean_abs_contribution` | manual | `notebooks/02_train.ipynb` |

## Out of scope
- Explicación por cliente en la aplicación → VS-009.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Gabriel (turno 1)
