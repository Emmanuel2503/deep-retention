---
id: VS-009
title: Explicar el riesgo de un cliente
status: ready
story: US-007
covers: [AC-01]
adrs: [ADR-0002]
depends_on: [VS-004, VS-005, VS-007]
---

# VS-009: Explicar el riesgo de un cliente

## Goal
Al consultar un cliente, existente o nuevo, el Ejecutivo de cuentas ve un gráfico de cascada con las variables que suben o bajan su Probabilidad de fuga, cada una con el valor del cliente, desde la Probabilidad de fuga media de referencia hasta la del cliente.

## Approach
`src/explain.py` agrega `customer_contributions`, que usa el explicador de VS-004 (sobre la Probabilidad de fuga calibrada) con una fila (`explainer.contributions(row)`, ya por variable original) y toma el valor base de `explainer.base_value`. La app crea el explicador una vez con `st.cache_resource`, con el fondo `background_sample(portfolio)` de VS-004 sobre la Cartera puntuada que devuelve `load_portfolio()`. Debajo de los resultados se muestran un gráfico de cascada (matplotlib con `st.pyplot`) desde el valor base hasta la Probabilidad de fuga del cliente, y una tabla con las mismas contribuciones. Las etiquetas usan nombres en español con el valor original ("Edad = 52").

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `customer_contributions` | `src/explain.py` |
| UI | Gráfico de cascada y tabla de contribuciones | `app/app.py` |

## Contracts
```
# src/explain.py
Contribution = TypedDict{feature: str, value: object, contribution: float}
customer_contributions(explainer, row: DataFrame) -> {"base_value": float, "contributions": list[Contribution]}
  # una entrada por variable original, ordenadas por |contribution| descendente;
  # base_value + Σ contribution = Probabilidad de fuga calibrada del cliente

# app/app.py (presentación)
FEATURE_LABELS = {"CreditScore": "Puntaje crediticio", "Geography": "País", "Gender": "Género",
  "Age": "Edad", "Tenure": "Antigüedad", "Balance": "Saldo", "NumOfProducts": "Productos",
  "HasCrCard": "Tiene tarjeta", "IsActiveMember": "Miembro activo",
  "EstimatedSalary": "Salario estimado", "Satisfaction Score": "Satisfacción",
  "Card Type": "Tipo de tarjeta", "Point Earned": "Puntos"}
st.dataframe columnas ["Variable", "Contribución"]   # Variable = "Edad = 52"
st.caption: "Probabilidad de fuga media de referencia: 0.xx → Probabilidad de fuga del cliente: 0.xx"
```

## Tasks
- [ ] **T-01:** Implementar `customer_contributions` → AC-01
- [ ] **T-02:** Crear el explicador en caché en la app y mostrar gráfico, tabla y caption para clientes buscados y del formulario → AC-01

## Tests
Con la Cartera puntuada real (sin `DEEP_RETENTION_PORTFOLIO`): en la Cartera de ejemplo las probabilidades son fijas y no las produce la red, así que la suma de contribuciones no coincidiría con ellas.

| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | Buscar 15634602 (primer cliente del dataset) y enviar un cliente por formulario muestran, en ambos casos, una tabla de contribuciones con una fila por variable con formato "<etiqueta> = <valor original>", ordenada por valor absoluto descendente; el valor base más la suma de la columna "Contribución" es igual (± 0.01) a la Probabilidad de fuga que muestra el Buscador | manual | app, pestaña "Buscador" |

## Out of scope
- Explicaciones en texto.

## Open questions
None.

## Done when
- [ ] All tasks checked
- [ ] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Daniel (turno 4)
