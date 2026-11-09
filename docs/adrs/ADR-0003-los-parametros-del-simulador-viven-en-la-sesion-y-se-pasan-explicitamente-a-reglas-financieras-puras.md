---
id: ADR-0003
title: Los parámetros del simulador viven en la sesión y se pasan explícitamente a reglas financieras puras
status: superseded
date: 2026-11-08
supersedes: []
superseded_by: ADR-0007
---

# ADR-0003: Los parámetros del simulador viven en la sesión y se pasan explícitamente a reglas financieras puras

## Context
El Buscador por cliente, el Panel de cartera y la matriz de segmentos deben usar los parámetros vigentes del Simulador de parámetros (SRS/BR-08). Esos parámetros duran solo la sesión y se pueden restablecer a los valores base (EP-004/BR-04). Si cada vista leyera los parámetros de un lugar distinto, o las reglas financieras dependieran de variables globales, las vistas podrían mostrar cifras incoherentes entre sí y las reglas no se podrían probar aisladas.

## Applies to
- `src/finance.py` y `app/app.py`.

## Decision
- `src/finance.py` define un `Params` inmutable con todos los parámetros (Margen del cliente e Incentivos) y una constante `DEFAULT_PARAMS` con los valores base de SRS/BR-03 y SRS/BR-04.
- Todas las funciones de `src/finance.py` son puras: reciben `params` como argumento explícito y no leen estado global, archivos ni Streamlit.
- La aplicación es un único script `app/app.py` con tres pestañas: "Buscador", "Cartera" y "Simulador". Los parámetros vigentes se guardan en `st.session_state["params"]`, se inicializan con `DEFAULT_PARAMS` si no existen y se pasan a cada llamada de `src/finance.py` desde las tres pestañas.
- Restablecer los valores base es asignar `DEFAULT_PARAMS` a `st.session_state["params"]`.

### Roles and responsibilities
- `Incentive` (`src/finance.py`): nombre, costo y Efectividad de un Incentivo.
- `Params` (`src/finance.py`): Spread, comisiones, Costo de servicio y tupla de `Incentive`.
- `DEFAULT_PARAMS` (`src/finance.py`): valores base.
- `st.session_state["params"]` (`app/app.py`): única fuente de los parámetros vigentes en la sesión.

### Forbidden
- **F-01:** No importar `streamlit` en `src/`.
- **F-02:** No leer los parámetros de una variable global de módulo dentro de las funciones de `src/finance.py`; siempre por argumento.
- **F-03:** No guardar parámetros del Simulador en disco ni en variables fuera de `st.session_state`.

### Canonical example
```python
# src/finance.py
@dataclass(frozen=True)
class Incentive:
    name: str
    cost: float
    effectiveness: float          # 0..1

@dataclass(frozen=True)
class Params:
    spread: float = 0.02
    fee_per_product: float = 50.0
    fee_card: float = 30.0
    service_cost: float = 60.0
    incentives: tuple[Incentive, ...] = (
        Incentive("Gestor VIP y tarifa plana", 500.0, 0.40),
        Incentive("Exoneración de comisiones", 150.0, 0.30),
        Incentive("Bonificación transaccional", 50.0, 0.20),
    )

DEFAULT_PARAMS = Params()

# app/app.py
params = st.session_state.setdefault("params", DEFAULT_PARAMS)
scored = score_portfolio(portfolio, params)
```
Reference implementation: `src/finance.py`

## Alternatives considered
- **Aplicación multipágina de Streamlit:** también comparte `session_state`, pero `AppTest` prueba un script por vez y complica verificar que un cambio del Simulador se refleje en el Buscador.
- **Parámetros en un archivo de configuración editable:** contradice que duren solo la sesión (EP-004/BR-04).

## Consequences
- **Positive:** las reglas financieras se prueban como funciones puras; las tres pestañas son coherentes por construcción; restablecer es una sola asignación.
- **Negative / costs:** cada llamada a `src/finance.py` debe pasar `params`, y la app recalcula la Cartera completa en cada interacción (barato con 10,000 filas).

## How it is enforced
- **Automated:** `pytest tests/test_architecture.py`: comprueba que ningún archivo de `src/` importe `streamlit` → F-01.
- **Review checklist:**
  - [ ] ¿Cada función nueva de `src/finance.py` recibe `params` por argumento? (F-02)
  - [ ] ¿La app lee los parámetros solo de `st.session_state["params"]`? (F-03)
