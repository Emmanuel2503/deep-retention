"""Factores de fuga globales con SHAP (US-004).

Explica la Probabilidad de fuga calibrada (SRS/TR-06, SRS/BR-07): la función explicada es
`ChurnPredictor.predict` (preprocesador, red y calibrador) sobre las variables originales.
Cada variable original es un solo jugador de SHAP: las columnas one-hot de una variable
categórica cambian juntas, así que la red nunca evalúa codificaciones imposibles (dos
países a la vez o ninguno) y no hace falta sumar contribuciones por columna.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import shap

from src.config import MODELS_DIR, REPORTS_DIR, SEED
from src.evaluate import test_split
from src.inference import ChurnPredictor

BACKGROUND_SIZE = 100
GLOBAL_SAMPLE_SIZE = 500
SUMMARY_FIGURE = "shap_summary.png"
GLOBAL_FACTORS_FILE = "global_factors.json"


def shap_summary_path(reports_dir=REPORTS_DIR) -> Path:
    return Path(reports_dir) / "figures" / SUMMARY_FIGURE


def background_sample(portfolio: pd.DataFrame, n: int = BACKGROUND_SIZE, seed: int = SEED) -> pd.DataFrame:
    """Clientes de entrenamiento como fondo de SHAP: una muestra de n, o todos si hay menos."""
    train = portfolio[portfolio["split"] == "train"]
    if train.empty:
        raise ValueError(
            'La Cartera puntuada no tiene clientes de entrenamiento (split == "train") para el fondo de SHAP.'
        )
    if len(train) <= n:
        return train
    return train.sample(n=n, random_state=seed)


class ChurnExplainer:
    """KernelExplainer de SHAP sobre la Probabilidad de fuga calibrada de un ChurnPredictor."""

    def __init__(self, predictor: ChurnPredictor, background: pd.DataFrame):
        self.predictor = predictor
        self.features: list[str] = list(predictor.features)
        background = background[self.features]
        # KernelExplainer entrega a la función filas numpy de tipo object; se restauran los tipos.
        self._dtypes = background.dtypes
        self.kernel = shap.KernelExplainer(self._predict, background)
        self.base_value = float(self.kernel.expected_value)

    def _predict(self, X: np.ndarray) -> np.ndarray:
        rows = pd.DataFrame(X, columns=self.features).astype(self._dtypes)
        return self.predictor.predict(rows)

    def contributions(self, sample: pd.DataFrame) -> pd.DataFrame:
        """Contribución SHAP de cada cliente (filas) a su Probabilidad de fuga, por variable original."""
        # l1_reg=False: sin selección de variables, todas reciben su contribución.
        values = self.kernel.shap_values(sample[self.features], l1_reg=False, silent=True)
        values = np.asarray(values).reshape(len(sample), len(self.features))
        return pd.DataFrame(values, columns=self.features, index=sample.index)


def build_explainer(predictor: ChurnPredictor, background: pd.DataFrame) -> ChurnExplainer:
    return ChurnExplainer(predictor, background)


def factors_from_contributions(contributions: pd.DataFrame) -> list[dict]:
    mean_abs = contributions.abs().mean().sort_values(ascending=False)
    return [{"feature": name, "mean_abs_contribution": float(value)} for name, value in mean_abs.items()]


def global_factors(explainer: ChurnExplainer, sample: pd.DataFrame) -> list[dict]:
    """Una entrada por variable original, de mayor a menor contribución media absoluta."""
    return factors_from_contributions(explainer.contributions(sample))


def run_global_explanation(models_dir=MODELS_DIR, reports_dir=REPORTS_DIR, sample_size: int = GLOBAL_SAMPLE_SIZE) -> list[dict]:
    import matplotlib.pyplot as plt

    models_dir = Path(models_dir)
    figure_path = shap_summary_path(reports_dir)
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    portfolio = pd.read_csv(models_dir / "portfolio_scored.csv")
    test = test_split(portfolio)
    sample = test.sample(n=min(sample_size, len(test)), random_state=SEED)

    explainer = build_explainer(ChurnPredictor.load(models_dir), background_sample(portfolio))
    contributions = explainer.contributions(sample)
    factors = factors_from_contributions(contributions)

    with open(models_dir / GLOBAL_FACTORS_FILE, "w", encoding="utf-8") as f:
        json.dump(factors, f, indent=2, ensure_ascii=False)

    # Figura nueva: summary_plot dibuja sobre la figura actual de pyplot.
    fig = plt.figure()
    shap.summary_plot(
        contributions.to_numpy(), feature_names=list(contributions.columns), plot_type="bar", show=False
    )
    fig.axes[0].set_xlabel("Contribución media absoluta a la Probabilidad de fuga")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return factors
