---
id: ADR-0002
title: La aplicación lee una Cartera puntuada precalculada
status: accepted
date: 2026-11-08
supersedes: []
superseded_by: none
---

# ADR-0002: La aplicación lee una Cartera puntuada precalculada

## Context
El Buscador por cliente y el Panel de cartera necesitan la Probabilidad de fuga de los 10,000 clientes, y el Simulador de parámetros recalcula las decisiones en cada cambio sin que la Probabilidad de fuga cambie (EP-004/BR-01). Volver a ejecutar la red sobre toda la Cartera en cada interacción es lento e innecesario. Además, la verificación manual de la aplicación necesita clientes con una Probabilidad de fuga fija (por ejemplo 0.80) para comprobar los montos de los criterios de aceptación, cosa imposible si la probabilidad sale siempre de la red real.

## Applies to
- `src/train.py` (produce la Cartera puntuada), `src/inference.py` (la lee) y `app/` (la consume).

## Decision
- Al terminar el entrenamiento, `src/train.py` puntúa a todos los clientes del dataset y guarda la Cartera puntuada en `models/portfolio_scored.csv`, versionada junto a los demás artefactos.
- La aplicación obtiene la Probabilidad de fuga de los clientes existentes leyendo la Cartera puntuada con `src.inference.load_portfolio()`. Solo ejecuta la red para clientes nuevos ingresados por formulario y para las explicaciones por cliente.
- `load_portfolio()` lee la ruta de la variable de entorno `DEEP_RETENTION_PORTFOLIO` si existe; si no, usa `models/portfolio_scored.csv`. Para verificar los criterios de aceptación se apunta a una Cartera puntuada de ejemplo en `data/fixtures/`.

### Roles and responsibilities
- `src/train.py`: escribe `models/portfolio_scored.csv`.
- `src/inference.py`: `load_portfolio()` y `ChurnPredictor` para clientes nuevos.
- `src/config.py`: `portfolio_path()` resuelve la variable de entorno o la ruta por defecto.
- `data/fixtures/*.csv`: Carteras puntuadas pequeñas con probabilidades fijas para la verificación manual.

Columnas de la Cartera puntuada (contrato):
```
CustomerId:int, CreditScore:int, Geography:str, Gender:str, Age:int, Tenure:int,
Balance:float, NumOfProducts:int, HasCrCard:int(0|1), IsActiveMember:int(0|1),
EstimatedSalary:float, Satisfaction Score:int, Card Type:str, Point Earned:int,
Exited:int(0|1), split:str("train"|"val"|"test"), p_raw:float[0,1], p_churn:float[0,1]
```
`p_churn` es la Probabilidad de fuga calibrada (SRS/BR-07); `p_raw` es la salida de la red sin calibrar.

### Forbidden
- **F-01:** No llamar a la red sobre la Cartera completa desde `app/`.
- **F-02:** No leer `models/portfolio_scored.csv` con una ruta fija desde `app/`; usar siempre `load_portfolio()`.

### Canonical example
```python
# app/app.py
from src.inference import load_portfolio
portfolio = load_portfolio()          # respeta DEEP_RETENTION_PORTFOLIO
row = portfolio.loc[portfolio.CustomerId == customer_id]
```
Reference implementation: `src/inference.py`

## Alternatives considered
- **Predecir en vivo la Cartera al iniciar la app (con caché):** arranque lento en Streamlit Cloud e imposible fijar probabilidades para verificar montos.
- **Inyectar un predictor falso:** obliga a modificar la app para verificarla; una variable de entorno con un archivo de ejemplo es más simple.

## Consequences
- **Positive:** la app arranca rápido; el Simulador recalcula con pandas sobre 10,000 filas; la verificación manual comprueba montos exactos.
- **Negative / costs:** la Cartera puntuada debe regenerarse y versionarse cada vez que se reentrena la red; si no, queda desactualizada respecto de `model.keras`.

## How it is enforced
- **Automated:** None (sin pruebas automatizadas, ADR-0006).
- **Review checklist:**
  - [ ] `grep -rn "portfolio_scored.csv" app/` no devuelve nada (F-02)
  - [ ] ¿Se regeneró `models/portfolio_scored.csv` en el mismo commit que `models/model.keras`?
  - [ ] ¿La app llama a `ChurnPredictor.predict` solo para el formulario y las explicaciones? (F-01)
