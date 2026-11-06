# Deep Retention

Sistema de retención selectiva de clientes bancarios. Una red neuronal (MLP) estima la probabilidad de fuga de cada cliente y una regla financiera decide si conviene o no invertir en retenerlo.

📄 **[Informe ejecutivo (PDF)](reports/informe_ejecutivo.pdf)**

## Problema

Retener a todos los clientes por igual reduce el margen del banco. Este proyecto solo autoriza una acción de retención si la ganancia neta esperada es positiva:

```
Ganancia Neta Esperada = (P_fuga × Efectividad × Margen) − Costo_incentivo
```

Si el resultado es mayor que cero, se recomienda el incentivo con mayor ganancia. Si ningún incentivo es rentable, el cliente se clasifica como **Salida Permitida**.

## Dataset

[Bank Customer Churn (Kaggle)](https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn): 10,000 clientes, 20.4% de abandono.

- **Excluidas:** `RowNumber`, `CustomerId`, `Surname` (identificadores) y `Complain` (fuga de datos: correlación de 0.996 con `Exited`).
- **Escaladas:** [lista de variables numéricas].
- **One-Hot:** `Geography`, `Gender`, `Card Type`.

## Modelo

- Perceptrón multicapa: [Dense 64 + BatchNorm + Dropout → Dense 32 + Dropout → Sigmoide].
- Manejo del desbalance con ponderación de clases.
- Early Stopping sobre `val_loss`.
- Framework: [Keras / PyTorch].

| Métrica | Valor |
|---|---|
| ROC-AUC | [valor] |
| PR-AUC | [valor] |
| Calibración (Brier) | [valor] |

## Estructura del repositorio

```
deep-retention/
├── app/            # aplicación Streamlit
├── data/           # dataset
├── models/         # pesos, scaler y encoder
├── notebooks/      # exploración (EDA)
├── reports/        # informe ejecutivo en PDF
├── src/            # preprocesamiento, entrenamiento, inferencia, reglas financieras
├── requirements.txt
└── README.md
```

## Instalación y uso

```bash
git clone https://github.com/[usuario]/deep-retention.git
cd deep-retention
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Entrenar el modelo (opcional, ya hay pesos guardados en `models/`):

```bash
python src/train.py
```

Lanzar la aplicación:

```bash
streamlit run app/app.py
```

## Aplicación

- **Buscador por cliente:** probabilidad de fuga, ganancia esperada y decisión sugerida.
- **Panel de cartera:** capital en riesgo, capital rescatable, inversión y ROI.
- **Simulador:** ajuste de costos y efectividad de las campañas.

## Supuestos financieros

| Incentivo | Costo | Efectividad |
|---|---|---|
| [Gestor VIP + tarifa plana] | $[
