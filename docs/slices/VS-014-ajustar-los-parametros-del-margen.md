---
id: VS-014
title: Ajustar los parámetros del margen
status: done
story: US-012
covers: [AC-01, AC-02]
adrs: [ADR-0007]
depends_on: [VS-013]
---

# VS-014: Ajustar los parámetros del margen

## Goal
En la pestaña "Simulador", la Dirección de Estrategia cambia el Spread, las comisiones o el Costo de servicio y ve recalculados los Márgenes del cliente, la mediana de niveles de valor, los Segmentos, las Decisiones de retención y los indicadores.

## Approach
Igual que VS-013: cuatro `number_input` más (Spread en %, Comisión por producto, Comisión por tarjeta y Costo de servicio), inicializados con `widget_defaults` y con `on_change=on_margin_change`, un callback que valida los cuatro valores con `validate_margin_params` y, si son válidos, reemplaza `params` con `dataclasses.replace`; si no, guarda los mensajes en `sim_errors`. Como `score_portfolio` recalcula el margen y `value_level` en cada ejecución, la mediana se recalcula sola (US-012/BF-03).

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `validate_margin_params` | `src/validation.py` |
| Domain | Claves del margen en `widget_defaults` | `src/finance.py` |
| UI | Entradas del margen en "Simulador" y callback | `app/app.py` |

## Contracts
```
# src/validation.py
validate_margin_params(spread_pct: float, fee_per_product: float, fee_card: float,
                       service_cost: float) -> dict[str, str]     # campo → mensaje; {} si es válido

# src/finance.py
widget_defaults(params) agrega {"spread": 2, "fee_per_product": 50, "fee_card": 30, "service_cost": 60}
  # (con DEFAULT_PARAMS; spread en %)

# app/app.py, pestaña "Simulador"
number_input key="spread" (%), "fee_per_product", "fee_card", "service_cost", on_change=on_margin_change
```

## Tasks
- [x] **T-01:** Implementar `validate_margin_params` y extender `widget_defaults` → AC-02
- [x] **T-02:** Crear las entradas del margen y actualizar `params` en el callback → AC-01

## Tests
Con `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv` (ADR-0006).

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Poner `spread` = 0 y buscar 1001 muestra Margen $70.00 y Decisión "Salida Permitida" | manual | app, pestañas "Simulador" y "Buscador" |
| AC-02 | Poner `service_cost` = -10 muestra un error con el rango permitido, y los indicadores de "Cartera" quedan iguales a los iniciales | manual | app, pestañas "Simulador" y "Cartera" |

## Out of scope
- Restablecer valores base → VS-015.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [x] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Emmanuel (turno 3)
