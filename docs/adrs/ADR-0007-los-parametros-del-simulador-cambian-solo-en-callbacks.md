---
id: ADR-0007
title: Los parámetros del simulador viven en la sesión, cambian solo en callbacks y se pasan explícitamente a reglas financieras puras
status: accepted
date: 2026-11-08
supersedes: [ADR-0003]
superseded_by: none
---

# ADR-0007: Los parámetros del simulador viven en la sesión, cambian solo en callbacks y se pasan explícitamente a reglas financieras puras

## Context
Reemplaza a ADR-0003: mantiene su decisión y agrega dos cosas que se detectaron en la revisión de los specs, antes de escribir código: los parámetros solo cambian en callbacks, y no toda función de `src/finance.py` necesita `params`, solo las que dependen de ellos.

El Buscador por cliente, el Panel de cartera y la matriz de segmentos deben usar los parámetros vigentes del Simulador de parámetros (SRS/BR-08). Esos parámetros duran solo la sesión y se pueden restablecer a los valores base (EP-004/BR-04). Si cada vista leyera los parámetros de un lugar distinto, o las reglas financieras dependieran de variables globales, las vistas podrían mostrar cifras incoherentes entre sí y las reglas no se podrían verificar aisladas. Además, Streamlit ejecuta el script de arriba abajo: si la pestaña "Simulador" actualizara los parámetros en el cuerpo del script, "Buscador" y "Cartera", que se dibujan antes, mostrarían los parámetros anteriores hasta la siguiente interacción.

## Applies to
- `src/finance.py` y `app/app.py`.

## Decision
- `src/finance.py` define un `Params` inmutable con todos los parámetros (Margen del cliente e Incentivos) y una constante `DEFAULT_PARAMS` con los valores base de SRS/BR-03 y SRS/BR-04.
- Las funciones de `src/finance.py` son puras: no leen estado global, archivos ni Streamlit, y toda función que depende de los parámetros los recibe como argumento explícito `params`.
- La aplicación es un único script `app/app.py` con tres pestañas: "Buscador", "Cartera" y "Simulador". Los parámetros vigentes se guardan en `st.session_state["params"]`, se inicializan con `DEFAULT_PARAMS` si no existen y se pasan a cada llamada de `src/finance.py` desde las tres pestañas.
- Las entradas del Simulador cambian `st.session_state["params"]` solo dentro de callbacks (`on_change` / `on_click`), que Streamlit ejecuta antes del script; así las tres pestañas usan los parámetros nuevos en la misma ejecución. Los mensajes de validación que produce un callback se guardan en `st.session_state["sim_errors"]` y la pestaña "Simulador" los muestra.
- Restablecer los valores base es asignar `DEFAULT_PARAMS` a `st.session_state["params"]` en el callback del botón.

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
- **Aplicación multipágina de Streamlit:** también comparte `session_state`, pero reparte las vistas en scripts distintos y complica comprobar que un cambio del Simulador se refleje en el Buscador.
- **Parámetros en un archivo de configuración editable:** contradice que duren solo la sesión (EP-004/BR-04).

## Consequences
- **Positive:** las reglas financieras se pueden ejecutar y revisar como funciones puras; las tres pestañas son coherentes por construcción; restablecer es una sola asignación.
- **Negative / costs:** cada llamada a `src/finance.py` debe pasar `params`, y la app recalcula la Cartera completa en cada interacción (barato con 10,000 filas).

## How it is enforced
- **Automated:** None (sin pruebas automatizadas, ADR-0006).
- **Review checklist:**
  - [ ] `grep -rnE "(import|from) streamlit" src/` no devuelve nada (F-01)
  - [ ] ¿Los `params` cambian solo en callbacks y no en el cuerpo del script?
  - [ ] ¿Cada función nueva de `src/finance.py` que usa parámetros los recibe por argumento? (F-02)
  - [ ] ¿La app lee los parámetros solo de `st.session_state["params"]`? (F-03)
