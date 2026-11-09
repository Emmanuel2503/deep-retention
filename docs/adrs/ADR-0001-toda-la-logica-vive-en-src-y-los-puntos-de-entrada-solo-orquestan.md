---
id: ADR-0001
title: Toda la lógica vive en src y los puntos de entrada solo orquestan
status: accepted
date: 2026-11-08
supersedes: []
superseded_by: none
---

# ADR-0001: Toda la lógica vive en src y los puntos de entrada solo orquestan

## Context
El modelo se entrena en Jupyter notebooks en Google Colab (SRS/TR-02), pero la rúbrica exige código modular, inferencia separada del entrenamiento y reproducibilidad (SRS/TR-09, SRS/NFR-01). La lógica escrita dentro de un notebook no se puede reutilizar ni ejecutar fuera de Colab, se duplica entre el notebook, `train.py` y la aplicación, y acaba divergiendo.

## Applies to
- Whole system: `notebooks/`, `src/train.py`, `app/` y `src/`.

## Decision
- Toda la lógica (carga y preparación de datos, construcción y entrenamiento de la red, calibración, evaluación, explicabilidad, reglas financieras y validación de entradas) se implementa como funciones o clases en módulos de `src/`.
- Los notebooks, `src/train.py` y `app/app.py` solo importan de `src/`, llaman a esas funciones y muestran o guardan sus resultados.
- En Colab, el notebook clona el repositorio, instala `requirements.txt` y agrega la raíz del repositorio a `sys.path` antes de importar `src`.
- La aplicación importa solo `src.config`, `src.inference`, `src.explain`, `src.finance` y `src.validation`, nunca los módulos de entrenamiento.

### Roles and responsibilities
- `src/config.py`: rutas del repositorio (dataset, `models/`, `reports/`) y semilla.
- `src/preprocessing.py`: carga del dataset, variables excluidas, particiones y preprocesador.
- `src/model.py`: arquitectura de la red, entrenamiento y calibración.
- `src/train.py`: orquesta el entrenamiento completo y exporta los artefactos; el notebook `02_train` llama a su misma función.
- `src/evaluate.py`: métricas sobre los Clientes de prueba y criterio de aceptación.
- `src/explain.py`: Factores de fuga globales y explicación por cliente.
- `src/inference.py`: carga de artefactos, predicción y Cartera puntuada (ADR-0002).
- `src/finance.py`: reglas financieras puras (ADR-0007).
- `src/validation.py`: límites de negocio de las entradas.
- `notebooks/`, `app/app.py`: solo orquestación y presentación.

### Forbidden
- **F-01:** No definir funciones ni clases con lógica de negocio o de modelo dentro de los notebooks ni de `app/app.py`; los helpers de presentación de la app (formatear y dibujar) sí se permiten.
- **F-02:** No importar `src.train`, `src.model` ni `src.evaluate` desde `app/`.
- **F-03:** No usar rutas absolutas ni rutas de Colab (`/content/...`) dentro de `src/`; todas salen de `src/config.py`.

### Canonical example
```python
# notebooks/02_train.ipynb (celda)
from src.train import run_training
result = run_training()
result.metrics
```
Reference implementation: `src/train.py`

## Alternatives considered
- **Todo en notebooks:** la rúbrica lo califica como "Competente" (código en un único cuaderno) y no se puede probar.
- **Paquete instalable (`pip install -e .`):** más configuración de la necesaria para un proyecto académico; `sys.path` basta.

## Consequences
- **Positive:** la lógica se ejecuta y se revisa sin Colab; notebook, script y app comparten exactamente el mismo código.
- **Negative / costs:** cada cambio de lógica obliga a editar `src/` y volver a clonar o hacer pull en Colab.

## How it is enforced
- **Automated:** None (sin pruebas automatizadas, ADR-0006).
- **Review checklist:**
  - [ ] `grep -rnE "src\.(train|model|evaluate)" app/` no devuelve nada (F-02)
  - [ ] `grep -rn "/content/" src/` no devuelve nada (F-03)
  - [ ] ¿Las celdas nuevas del notebook solo llaman funciones de `src/`? (F-01)
  - [ ] ¿`app/app.py` solo contiene presentación? (F-01)
