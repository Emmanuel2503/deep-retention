---
id: VS-005
title: Consultar un cliente y ver su decisión de retención
status: ready
story: US-005
covers: [AC-01, AC-02, AC-04]
adrs: [ADR-0002, ADR-0007]
depends_on: [VS-001]
---

# VS-005: Consultar un cliente y ver su decisión de retención

## Goal
El Ejecutivo de cuentas abre la aplicación, escribe el identificador de un cliente en la pestaña "Buscador" y ve su Probabilidad de fuga, Margen del cliente, Ganancia neta esperada de cada Incentivo, Segmento y Decisión de retención.

## Approach
Tracer bullet de la aplicación. No necesita el modelo: se construye y verifica con la Cartera puntuada de ejemplo `data/fixtures/portfolio_cases.csv`, que sigue el contrato de columnas de ADR-0002, así que puede empezar en cuanto VS-001 está en `main`, en paralelo con VS-002. `src/config.py` agrega `portfolio_path()` y `src/inference.py` agrega `load_portfolio()` (ADR-0002). `src/finance.py` implementa las reglas financieras puras (SRS/BR-01 a BR-05) con `Params` (ADR-0007). `app/app.py` crea las tres pestañas, inicializa `st.session_state["params"]`, carga la Cartera puntuada con `load_portfolio()`, la puntúa con `score_portfolio(portfolio, params)` y, en "Buscador", muestra la fila del cliente buscado. Las pestañas "Cartera" y "Simulador" quedan vacías hasta VS-010 y VS-013.

## Changes
| Layer | Change | Location |
|---|---|---|
| Config | `portfolio_path()` con la variable de entorno `DEEP_RETENTION_PORTFOLIO` | `src/config.py` |
| Inference | `load_portfolio` | `src/inference.py` |
| Domain | `Incentive`, `Params`, `DEFAULT_PARAMS`, margen, ganancias, nivel de valor, segmento, decisión, `score_portfolio` | `src/finance.py` |
| UI | App con pestañas "Buscador", "Cartera", "Simulador"; búsqueda por identificador; formato de montos y probabilidad (SRS/BR-09) | `app/app.py` |
| Data | Cartera puntuada de ejemplo | `data/fixtures/portfolio_cases.csv` |

## Contracts
```
# src/config.py
portfolio_path() -> Path   # env DEEP_RETENTION_PORTFOLIO o MODELS_DIR / "portfolio_scored.csv"

# src/inference.py
load_portfolio(path: Path | None = None) -> DataFrame   # None → config.portfolio_path()

# src/finance.py  (Incentive, Params, DEFAULT_PARAMS según ADR-0007)
SALIDA_PERMITIDA = "Salida Permitida"
SIN_ACCION = "Sin Acción Requerida"
HIGH_RISK = 0.65
LOW_RISK = 0.30

customer_margin(balance, num_products, has_card, params) -> float | Series
expected_net_gains(p: float, margin: float, params) -> dict[str, float]   # nombre de Incentive → ganancia
value_level(margins: Series) -> Series            # "Superior" | "Medio" | "Bajo/Deficitario" (SRS/BR-05)
segment(p: float, level: str) -> str              # "A" | "B" | "C" | "D" | "E"
Decision = dataclass{label: str, incentive: Incentive | None, gains: dict[str, float]}
decide(p: float, margin: float, segment: str, params) -> Decision
  # label = nombre del Incentivo, SALIDA_PERMITIDA o SIN_ACCION (SRS/BR-02);
  # segment solo elige entre SALIDA_PERMITIDA y SIN_ACCION
score_portfolio(portfolio: DataFrame, params) -> DataFrame
  # agrega: margin, value_level, segment, decision, incentive_cost, incentive_effectiveness,
  #         expected_gain, gain__<nombre de cada Incentive>

# app/app.py: elementos de la interfaz
st.tabs(["Buscador", "Cartera", "Simulador"])
radio  key="search_mode"   opciones ["Cliente existente", "Cliente nuevo"]
text_input key="customer_id";  button key="search"
st.metric labels: "Probabilidad de fuga" ("0.80"), "Margen del cliente" ("$2,070.00"),
                  "Segmento" ("A".."E"), "Decisión de retención" (label)
st.dataframe columnas ["Incentivo", "Ganancia neta esperada"]    # valores numéricos
formato: montos "$1,234.56", negativos "-$10.00"; probabilidad "0.80"

# data/fixtures/portfolio_cases.csv (columnas de ADR-0002; resto de campos válidos)
CustomerId  Balance  NumOfProducts  HasCrCard  p_churn  split  Exited
1001        100000   2              1          0.80     test   1
1002        0        1              0          0.50     test   0
1003        100000   2              1          0.10     train  0
1004        0        1              0          0.70     val    1
1005        0        1              0          0.40     train  0
```

## Tasks
- [ ] **T-01:** Implementar `config.portfolio_path` e `inference.load_portfolio` → AC-01
- [ ] **T-02:** Implementar `customer_margin` y `expected_net_gains` → AC-01, AC-02
- [ ] **T-03:** Implementar `value_level`, `segment` y `decide` → AC-01, AC-02, AC-04
- [ ] **T-04:** Implementar `score_portfolio` → AC-01
- [ ] **T-05:** Crear `app/app.py` con las tres pestañas, el estado de sesión y la búsqueda por identificador → AC-01
- [ ] **T-06:** Crear `data/fixtures/portfolio_cases.csv` → none

## Tests
Todas las filas con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv venv/bin/streamlit run app/app.py` (ADR-0006).

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Buscar 1001 muestra Probabilidad de fuga 0.80, Margen $2,070.00, ganancias 162.40 / 346.80 / 281.20 y Decisión "Exoneración de comisiones" | manual | app, pestaña "Buscador" |
| AC-02 | Buscar 1002 muestra Margen -$10.00, las tres ganancias negativas y Decisión "Salida Permitida" | manual | app, pestaña "Buscador" |
| AC-04 | Buscar 1003 muestra ganancia de Bonificación transaccional -8.60, ninguna positiva, y Decisión "Sin Acción Requerida" | manual | app, pestaña "Buscador" |

## Out of scope
- Identificadores inexistentes o no numéricos (AC-03) → VS-006.
- Formulario de cliente nuevo → VS-007.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Ainhoa (turno 2)
