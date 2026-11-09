---
id: ADR-0006
title: No hay pruebas automatizadas y la verificación es manual
status: accepted
date: 2026-11-08
supersedes: []
superseded_by: none
---

# ADR-0006: No hay pruebas automatizadas y la verificación es manual

## Context
Los slices definían pruebas con pytest y `streamlit.testing.v1.AppTest`, y ADR-0001, ADR-0002 y ADR-0007 se hacían cumplir con `tests/test_architecture.py`. El equipo tiene 3 días para entregar y decidió no escribir ni mantener pruebas automatizadas. Algunas de las pruebas previstas, además, cargaban TensorFlow o SHAP, eran lentas y escribían en `models/`.

## Applies to
- Whole system.

## Decision
- No se crea `tests/`, no se instala pytest y no se escriben pruebas automatizadas.
- La tabla Tests de cada slice describe una verificación manual: qué hacer y qué valor se debe ver. Su columna Type es `manual` y su columna Location dice dónde se hace (notebook, pestaña de la app o archivo).
- Los montos de la aplicación se verifican con las Carteras puntuadas de ejemplo de `data/fixtures/`, cargadas con `DEEP_RETENTION_PORTFOLIO` (ADR-0002): `DEEP_RETENTION_PORTFOLIO=data/fixtures/portfolio_cases.csv venv/bin/streamlit run app/app.py`.
- Las comprobaciones automáticas de ADR-0001, ADR-0002 y ADR-0007 pasan a ser comandos `grep` de su review checklist.
- Un slice queda `done` cuando quien lo implementa y quien revisa el PR ejecutaron cada fila de su tabla Tests y obtuvieron el resultado esperado.

### Roles and responsibilities
- Responsable del slice: ejecuta la verificación manual antes de abrir el PR.
- Revisor del PR: la repite y ejecuta el review checklist de los ADRs aplicables.

### Forbidden
- **F-01:** No agregar pytest ni otro framework de pruebas a `requirements.txt`, ni crear `tests/`.

### Canonical example
```
| AC-01 | Con `portfolio_cases.csv`, buscar 1001 muestra Margen $2,070.00 y Decisión "Exoneración de comisiones" | manual | app, pestaña "Buscador" |
```
Reference implementation: None.

## Alternatives considered
- **Pruebas unitarias de `src/finance.py`, `src/validation.py` y de arquitectura:** baratas y protegen la lógica financiera; descartadas por decisión del equipo.
- **Las pruebas completas de los slices:** lentas (TensorFlow, SHAP) y frágiles para el plazo.

## Consequences
- **Positive:** menos código, dependencias y tiempo de CI; nada escribe en `models/` durante una verificación.
- **Excepción explícita:** esta decisión modificó la sección "How it is enforced" de ADR-0001 y ADR-0002, aunque estaban aceptados, porque solo cambia cómo se comprueban y todavía no había código. Los cambios de decisión de ADR-0003 se hicieron en un ADR nuevo (ADR-0007).
- **Negative / costs:** un error de lógica (por ejemplo, Efectividad en % en lugar de 0..1) o una regresión en un slice anterior solo se detecta si alguien repite a mano su verificación; conviene repetir las verificaciones de VS-005 y VS-010 tras cada cambio en `src/finance.py`.

## How it is enforced
- **Automated:** None.
- **Review checklist:**
  - [ ] ¿El revisor ejecutó cada fila de la tabla Tests del slice?
  - [ ] ¿El PR evita agregar `tests/` o pytest? (F-01)
