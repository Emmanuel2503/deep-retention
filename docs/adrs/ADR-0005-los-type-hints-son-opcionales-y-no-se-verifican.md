---
id: ADR-0005
title: Los type hints son opcionales y no se verifican
status: accepted
date: 2026-11-08
supersedes: [ADR-0004]
superseded_by: none
---

# ADR-0005: Los type hints son opcionales y no se verifican

## Context
ADR-0004 hacía obligatorios los type hints en la API pública de `src/` y los verificaba con mypy. El equipo tiene 3 días para entregar y trabaja con asistencia de IA. Un verificador de tipos agrega configuración, una dependencia y una comprobación más que puede bloquear los PR por errores de tipos de librerías como pandas, TensorFlow o Streamlit, sin aportar valor proporcional en un proyecto académico.

## Applies to
- Whole system.

## Decision
- Los type hints son opcionales en todo el código. Se pueden usar donde ayuden a leer el código (por ejemplo, en las firmas de los contratos de los slices), pero no son obligatorios.
- No se usa ningún verificador de tipos (mypy, pyright u otro): no se instala, no se configura y no se ejecuta en pruebas ni en la revisión de PR.
- Los contratos de los slices siguen escritos con tipos, como documentación de la forma de los datos.

### Roles and responsibilities
None.

### Forbidden
- **F-01:** No agregar mypy, pyright ni otro verificador de tipos a `requirements.txt` ni a la configuración del proyecto.
- **F-02:** No rechazar un PR por la falta de type hints.

### Canonical example
None.
Reference implementation: None.

## Alternatives considered
- **Mantener ADR-0004 (hints obligatorios y mypy no estricto):** descartado por decisión del equipo; agrega fricción sin valor suficiente para el plazo de entrega.
- **Hints obligatorios sin verificador:** sigue imponiendo una regla de revisión que el equipo no quiere.

## Consequences
- **Positive:** menos configuración y dependencias; los PR no se bloquean por tipos.
- **Negative / costs:** los errores de forma de los datos (por ejemplo, Efectividad en % en lugar de 0..1) solo se detectan al ejecutar o con los tests.

## How it is enforced
- **Automated:** None.
- **Review checklist:**
  - [ ] ¿El PR evita agregar un verificador de tipos? (F-01)
