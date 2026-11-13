---
id: VS-016
title: Generar el informe ejecutivo en PDF
status: done
story: US-013
covers: [AC-01, AC-02, AC-03, AC-04]
adrs: [ADR-0002]
depends_on: [VS-003, VS-004, VS-011, VS-012]
---

# VS-016: Generar el informe ejecutivo en PDF

## Goal
El Analista de datos genera `reports/informe_ejecutivo.pdf` desde `reports/informe.md`, con las cinco secciones de la plantilla completas y cifras que coinciden con el Panel de cartera con los parámetros base y con las métricas del modelo.

## Approach
`src/report.py` calcula las cifras del informe a partir de `load_portfolio()`, `score_portfolio(..., DEFAULT_PARAMS)`, `portfolio_kpis`, `segment_matrix`, `realized_roi`, `models/metrics.json` y `models/global_factors.json`, y `python -m src.report` las imprime en Markdown para copiarlas al informe. El Analista de datos redacta `reports/informe.md` siguiendo la plantilla, con líneas de cifras de formato fijo, e incluye las figuras de `reports/figures/`. La sección 3 incluye la matriz de segmentos y las explicaciones de US-013/BR-06 con las cifras impresas (inversión del Segmento D, clientes con Gestor VIP, tamaño del Segmento C). El PDF se genera con `pandoc --pdf-engine=xelatex`.

## Changes
| Layer | Change | Location |
|---|---|---|
| Domain | `report_numbers`, `report_numbers_markdown` y punto de entrada `__main__` | `src/report.py` |
| Docs | Informe en Markdown y PDF generado | `reports/informe.md`, `reports/informe_ejecutivo.pdf` |
| Docs | Comando de generación del PDF | `README.md` |

## Contracts
```
# src/report.py
report_numbers(models_dir=MODELS_DIR) -> dict
  # {"n_customers", "capital_at_risk", "capital_at_risk_critical", "rescuable_capital", "investment",
  #  "roi", "realized_roi_test",            # fracciones (2.312 = 231.2%); realized_roi sobre split == "test"
  #  "decision_counts", "segment_matrix",   # para la sección 3
  #  "roc_auc", "pr_auc", "brier_calibrated", "top_factors": [str, str, str]}
report_numbers_markdown(numbers: dict) -> str     # montos "$1,234.56", porcentajes con 1 decimal
# python -m src.report → imprime report_numbers_markdown(report_numbers())

# reports/informe.md: encabezados obligatorios
## 1. Resumen de Impacto Financiero y Retorno
## 2. Arquitectura de la Solución y Diagnóstico de Fuga
## 3. Matriz de Decisión Comercial y Rentabilidad
## 4. Operación de la Aplicación en Sucursales
## 5. Conclusiones y Próximos Pasos

# líneas de cifras con formato fijo (sección 1 y 2)
- Volumen Total de Clientes Analizados: 10,000
- Monto Total de Capital en Riesgo Crítico: $<capital_at_risk_critical>
- Capital Rescatable Estimado: $<rescuable_capital>
- Inversión Total en Campañas de Fidelización: $<investment>
- Retorno Sobre la Inversión (ROI): <roi>% (proyectado; > 0 por construcción)
- ROI Realizado con la Efectividad Supuesta (Clientes de Prueba): <realized_roi_test>%
Métricas de Diagnóstico Técnico: ROC-AUC: <x.xx> | Precision-Recall AUC: <x.xx> | Precisión de Calibración (Brier): <x.xxx>

# generación
pandoc reports/informe.md -o reports/informe_ejecutivo.pdf --pdf-engine=xelatex --resource-path=reports
```

## Tasks
- [x] **T-01:** Implementar `report_numbers`, `report_numbers_markdown` y `__main__` → AC-01, AC-02
- [x] **T-02:** Redactar `reports/informe.md` con las cinco secciones, cifras, figuras y la matriz → AC-01, AC-02
- [x] **T-03:** Redactar las secciones 4 y 5 con el procedimiento de 5 pasos, el mantenimiento trimestral y el piloto (US-013/BR-03..BR-05) → AC-03
- [x] **T-04:** Redactar en la sección 3 las explicaciones de US-013/BR-06 y en la sección 1 la nota de US-013/BR-07 → AC-04
- [x] **T-05:** Generar el PDF con pandoc y documentar el comando en el README → AC-01

## Tests
| AC | What the test verifies | Type | Location |
|---|---|---|---|
| AC-01 | `informe.md` contiene los cinco encabezados y ningún texto entre corchetes de la plantilla (`[...]`); sus seis líneas de cifras son idénticas a las que imprime `python -m src.report`; el Capital en riesgo crítico, la Inversión y el ROI coinciden con la pestaña "Cartera" con los valores base, y el ROI realizado con la misma pestaña filtrada; existe `informe_ejecutivo.pdf` | manual | `reports/informe.md`, terminal, app |
| AC-02 | La sección 2 contiene ROC-AUC, PR-AUC y Brier iguales a `metrics.json`, los tres primeros nombres de `global_factors.json` y la limitación de SHAP con las variables one-hot | manual | `reports/informe.md` |
| AC-03 | La sección 4 contiene cinco pasos numerados; la sección 5 contiene "trimestral", "0.05", "3 meses" y "grupo de control" | manual | `reports/informe.md` |
| AC-04 | La sección 3 explica, con las cifras que imprime `python -m src.report`, la inversión del Segmento D, la asignación de Gestor VIP y el tamaño del Segmento C; la sección 1 incluye el "ROI realizado con la Efectividad supuesta" y la nota de que el ROI es > 0 por construcción | manual | `reports/informe.md` |

## Out of scope
- Generar el informe desde la aplicación.

## Open questions
None.

## Done when
- [x] All tasks checked
- [x] Every AC in `covers` passes its test
- [ ] Enforcement checks of all applicable ADRs pass (listed here or whole-system)

## Responsable
Daniel (turno 4)
