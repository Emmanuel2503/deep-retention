---
id: ADR-0004
title: La API pública de src lleva type hints verificados con mypy no estricto
status: superseded
date: 2026-11-08
supersedes: []
superseded_by: ADR-0005
---

# ADR-0004: La API pública de src lleva type hints verificados con mypy no estricto

## Context
Los contratos de los slices definen las funciones de `src/` con tipos exactos (`Params`, `Decision`, `PortfolioKpis`, `TypedDict`), y esas funciones las usan otros módulos, la app, los notebooks y los tests, a menudo escritos por distintos miembros del equipo. Sin tipos en el código, los contratos solo viven en la documentación y los errores de forma (por ejemplo, Efectividad en % en lugar de 0..1) aparecen recién al ejecutar. Por otro lado, pandas, TensorFlow, SHAP y Streamlit tienen tipos incompletos, y un chequeo estricto exigiría mucho trabajo sin valor para un proyecto académico.

## Applies to
- Whole system: obligatorio en `src/`; opcional en `app/`, `notebooks/` y `tests/`.

## Decision
- Toda función, método y clase pública de `src/` (sin `_` inicial) declara los tipos de sus parámetros y de su retorno.
- Las estructuras de datos de los contratos son `@dataclass` (inmutables con `frozen=True` cuando sea posible) o `TypedDict`; no se devuelven `dict` sin tipar en la API pública.
- Se usa la sintaxis de Python 3.10 o superior: `X | None`, `list[str]`, `dict[str, float]`, con `from __future__ import annotations` en cada módulo de `src/`.
- Para DataFrames y arrays se usan `pd.DataFrame`, `pd.Series` y `np.ndarray`, sin tipos genéricos de columnas.
- La verificación es `mypy src/` sin modo estricto, configurado en `pyproject.toml` con `ignore_missing_imports = true` y `disallow_untyped_defs = true` solo para `src.*`.

### Roles and responsibilities
- `pyproject.toml` (raíz): configuración de mypy.
- `requirements.txt`: incluye `mypy`.

### Forbidden
- **F-01:** No dejar sin anotar una función pública de `src/`.
- **F-02:** No usar `Any` en la firma de una función pública de `src/`, salvo para valores de una celda de DataFrame (`value: object`).
- **F-03:** No silenciar errores de mypy con `# type: ignore` sin indicar el código del error y el motivo.

### Canonical example
```python
from __future__ import annotations

def expected_net_gains(p: float, margin: float, params: Params) -> dict[str, float]:
    return {i.name: p * i.effectiveness * margin - i.cost for i in params.incentives}
```
Reference implementation: `src/finance.py`

## Alternatives considered
- **Sin type hints:** los contratos quedan solo en la documentación y se pierde la ayuda del editor.
- **Type hints sin verificador:** documentan, pero divergen del código sin que nadie lo note.
- **`mypy --strict` en todo el código:** choca con los tipos incompletos de pandas, Keras y Streamlit; demasiado costo para un proyecto académico.

## Consequences
- **Positive:** los contratos de los slices quedan en el código, el editor autocompleta y mypy detecta errores de forma antes de ejecutar.
- **Negative / costs:** más texto en las firmas; algunas llamadas a librerías sin tipos devuelven `Any` y no se verifican.

## How it is enforced
- **Automated:** `mypy src/` (opción `disallow_untyped_defs` para `src.*`) → F-01, F-02.
- **Review checklist:**
  - [ ] ¿Las funciones públicas nuevas de `src/` tienen tipos de parámetros y de retorno? (F-01)
  - [ ] ¿Cada `# type: ignore` indica el código del error y el motivo? (F-03)
