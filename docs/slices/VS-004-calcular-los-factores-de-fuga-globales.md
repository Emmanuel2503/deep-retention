---
id: VS-004
title: Calcular los factores de fuga globales
status: done
story: US-004
covers: [AC-01]
adrs: []
depends_on: [VS-002]
---

# VS-004: Calcular los factores de fuga globales

## Goal
El Analista de datos obtiene desde el notebook la figura resumen SHAP y la lista ordenada de Factores de fuga, con una entrada por variable original, lista para el Informe ejecutivo.

## Approach
`src/explain.py` construye un `shap.KernelExplainer` sobre las variables originales, con `predictor.predict` (preprocesador, red y calibrador), así que explica la Probabilidad de fuga calibrada (SRS/TR-06, SRS/BR-07). Cada variable original es un solo jugador de SHAP: las columnas one-hot de una variable categórica cambian juntas, la red no evalúa codificaciones imposibles (dos países a la vez o ninguno) y no hay que sumar contribuciones por columna. Se calcula sin selección de variables (`l1_reg=False`), así que todas reciben contribución. El fondo lo elige `background_sample`: 100 clientes de `split == "train"` de la Cartera puntuada, con la semilla fija, o todos si hay menos. Se aplica a 500 Clientes de prueba (misma semilla) y se ordena por la media del valor absoluto de la contribución de cada variable. Guarda la figura y la lista. VS-009 reutiliza `background_sample` y `build_explainer` por cliente. Con KernelExplainer, el cálculo de 500 clientes tarda varios minutos en Colab.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `background_sample`, `ChurnExplainer`, `build_explainer`, `global_factors`, `shap_summary_path`, `run_global_explanation` | `src/explain.py` |
| Domain | `test_split` (filas de prueba, compartida con la evaluación) | `src/evaluate.py` |
| Notebook | Celda que llama a `run_global_explanation()` | `notebooks/02_train.ipynb` |
| Artifacts | Figura resumen y lista de factores | `reports/figures/shap_summary.png`, `models/global_factors.json` |

## Contracts
```
# src/explain.py
BACKGROUND_SIZE = 100
GLOBAL_SAMPLE_SIZE = 500
background_sample(portfolio: DataFrame, n: int = BACKGROUND_SIZE, seed: int = SEED) -> DataFrame
  # filas split == "train"; muestra de n con la semilla, o todas si hay menos de n;
  # ValueError si no hay ninguna
class ChurnExplainer:
  predictor: ChurnPredictor
  features: list[str]                       # predictor.features
  base_value: float                         # Probabilidad de fuga media de referencia
  contributions(sample: DataFrame) -> DataFrame   # una columna por variable original
build_explainer(predictor: ChurnPredictor, background: DataFrame) -> ChurnExplainer
  # KernelExplainer(predictor.predict sobre las variables originales, background[features])
global_factors(explainer: ChurnExplainer, sample: DataFrame) -> list[{"feature": str, "mean_abs_contribution": float}]
  # una entrada por variable original, orden descendente
run_global_explanation(models_dir=MODELS_DIR, reports_dir=REPORTS_DIR,
                       sample_size=GLOBAL_SAMPLE_SIZE) -> list[...]
  # escribe models_dir/global_factors.json y shap_summary_path(reports_dir)
shap_summary_path(reports_dir=REPORTS_DIR) -> Path   # reports_dir/figures/shap_summary.png
```

## Tasks
- [x] **T-01:** Implementar `background_sample` y `build_explainer` → AC-01
- [x] **T-02:** Implementar `global_factors` por variable original → AC-01
- [x] **T-03:** Implementar `run_global_explanation` y la figura; ejecutarla en Colab y versionar los artefactos → AC-01

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Tras `run_global_explanation()` en Colab: existe `shap_summary.png`, y `global_factors.json` tiene cada variable de `features.json["features"]` una sola vez, ordenadas de mayor a menor `mean_abs_contribution` | manual | `notebooks/02_train.ipynb` |

## Out of scope
- Explicación por cliente en la aplicación → VS-009.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Gabriel (turno 1)
