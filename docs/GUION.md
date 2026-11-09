# Guion de trabajo

Reparto de los slices (`docs/slices/`) entre los integrantes del equipo. Cada integrante tiene un turno con sus slices en orden, pero los turnos se solapan: un slice puede empezar en cuanto todos sus `depends_on` están en `main`. El turno 2 empieza con las Carteras puntuadas de ejemplo de `data/fixtures/` (ADR-0002), sin esperar al modelo; el turno 3 espera a VS-002 porque parte de sus verificaciones usa la Cartera puntuada real.

## Turnos

| Turno | Responsable | Slices, en orden | Puede empezar cuando | Qué entrega |
|---|---|---|---|---|
| 1 | Gabriel | VS-001 → VS-002 → VS-003 → VS-004 | Desde el inicio | Dataset en `data/`, modelo entrenado en Colab, Cartera puntuada, métricas y Factores de fuga globales en `models/` |
| 2 | Ainhoa | VS-005 → VS-006 → VS-007 → VS-008 | VS-001 en `main` (VS-007 espera a VS-002) | Esqueleto de la app, reglas financieras base y pestaña "Buscador" (identificador y formulario) |
| 3 | Emmanuel | VS-010 → VS-011 → VS-012 → VS-013 → VS-014 → VS-015 | VS-002 y VS-005 en `main` (algunas verificaciones usan la Cartera puntuada real) | Pestañas "Cartera" y "Simulador" |
| 4 | Daniel | VS-009 → VS-016 | VS-004 y VS-007 en `main` (VS-016 espera además a VS-003, VS-011 y VS-012) | Explicación SHAP por cliente e Informe ejecutivo en PDF |

## Detalle por slice

| Slice | Título | Historia | Depende de | Responsable |
|---|---|---|---|---|
| VS-001 | Cargar el dataset y excluir variables con fuga | US-001 | – | Gabriel |
| VS-002 | Entrenar, calibrar y exportar el modelo y la cartera puntuada | US-002 | VS-001 | Gabriel |
| VS-003 | Evaluar con clientes de prueba y aceptar o rechazar el modelo | US-003 | VS-002 | Gabriel |
| VS-004 | Calcular los factores de fuga globales | US-004 | VS-002 | Gabriel |
| VS-005 | Consultar un cliente y ver su decisión de retención | US-005 | VS-001 | Ainhoa |
| VS-006 | Rechazar identificadores inválidos | US-005 | VS-005 | Ainhoa |
| VS-007 | Evaluar un cliente nuevo por formulario | US-006 | VS-002, VS-005 | Ainhoa |
| VS-008 | Validar los límites de negocio del formulario | US-006 | VS-007 | Ainhoa |
| VS-009 | Explicar el riesgo de un cliente | US-007 | VS-004, VS-005, VS-007 | Daniel |
| VS-010 | Ver los indicadores de la cartera | US-008 | VS-002, VS-005 | Emmanuel |
| VS-011 | Ver la matriz por segmento | US-009 | VS-010 | Emmanuel |
| VS-012 | Filtrar solo clientes de prueba | US-010 | VS-011 | Emmanuel |
| VS-013 | Ajustar costo y efectividad de los incentivos | US-011 | VS-010 | Emmanuel |
| VS-014 | Ajustar los parámetros del margen | US-012 | VS-013 | Emmanuel |
| VS-015 | Restablecer valores base y parámetros por sesión | US-011 | VS-013, VS-014 | Emmanuel |
| VS-016 | Generar el informe ejecutivo en PDF | US-013 | VS-003, VS-004, VS-011, VS-012 | Daniel |

## Reglas

1. **Una rama por slice** (`vs-0XX-<slug>`), implementada con `/implement-spec VS-0XX`.
2. **Merge a `main` al terminar cada slice**, con el `status` del slice en `done`. Si no, `/implement-spec` de los slices que dependen de él se bloquea.
3. **Otra persona revisa el PR**: repite a mano cada fila de la tabla Tests del slice y ejecuta el review checklist de los ADRs aplicables (ADR-0006). No hay pruebas automatizadas.
4. **Solo Gabriel modifica `models/`.** El modelo se congela cuando VS-003 lo acepta; reentrenar después cambia las cifras de la Cartera y del Informe ejecutivo. Si VS-003 no lo acepta, no se versiona `models/` y VS-007, VS-009 y VS-016 esperan.
5. **`app/app.py` con una función por pestaña** (`render_buscador`, `render_cartera`, `render_simulador`) para evitar conflictos entre turnos que trabajan a la vez.
6. **Tras cada cambio en `src/finance.py`**, repetir las verificaciones de VS-005 y VS-010: sin pruebas automatizadas, es la única forma de detectar una regresión.
7. **Mientras se espera**, se puede avanzar trabajo sin dependencias: por ejemplo, Daniel puede redactar desde el inicio las secciones 4 y 5 del informe (VS-016, T-03), y quien terminó su turno revisa los PR de los demás.

## Qué recortar si no alcanza el tiempo

En este orden, de menor a mayor impacto en la rúbrica:

1. VS-015: restablecer valores base.
2. VS-014: parámetros del margen; VS-013 ya cubre el simulador de costos que pide el enunciado.
3. VS-009: SHAP por cliente; VS-004 ya cubre la explicabilidad global.
4. VS-006: mensajes de identificador inválido; si se recorta, la búsqueda debe al menos no lanzar una excepción con un texto no numérico (SRS/NFR-04).

No se recortan VS-001 a VS-005, VS-007, VS-008, VS-010 a VS-013 ni VS-016: cubren el modelo, la regla financiera, la validación de datos nuevos, el ROI realizado (VS-012, SRS/OBJ-03), las tres pestañas y el informe.
