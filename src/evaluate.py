"""Evaluación del modelo con los Clientes de prueba (US-003)."""
import json
from pathlib import Path
from typing import TypedDict

import pandas as pd
from matplotlib.figure import Figure
from sklearn.calibration import calibration_curve
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from src.config import MODELS_DIR, REPORTS_DIR
from src.preprocessing import TARGET

MIN_ROC_AUC = 0.80
MIN_PR_AUC = 0.55
RELIABILITY_BINS = 10
RELIABILITY_FIGURE = "reliability.png"
REQUIRED_COLUMNS = ["split", TARGET, "p_raw", "p_churn"]


class Metrics(TypedDict):
    n_test: int
    roc_auc: float
    pr_auc: float
    brier_raw: float
    brier_calibrated: float
    accepted: bool


def is_accepted(roc_auc: float, pr_auc: float, brier_raw: float, brier_calibrated: float) -> bool:
    """US-003/BR-01: umbrales de ROC-AUC y PR-AUC, y la calibración no empeora el Brier."""
    return roc_auc >= MIN_ROC_AUC and pr_auc >= MIN_PR_AUC and brier_calibrated <= brier_raw


def reliability_path(reports_dir=REPORTS_DIR) -> Path:
    return Path(reports_dir) / "figures" / RELIABILITY_FIGURE


def test_split(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Filas `split == "test"` de la Cartera puntuada; error si no hay ninguna."""
    if "split" not in portfolio.columns:
        raise ValueError("A la Cartera puntuada le falta la columna 'split'.")
    test = portfolio[portfolio["split"] == "test"]
    if test.empty:
        raise ValueError('La Cartera puntuada no tiene Clientes de prueba (split == "test").')
    return test


def _test_clients(portfolio: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in portfolio.columns]
    if missing:
        raise ValueError(f"A la Cartera puntuada le faltan las columnas {missing}.")
    test = test_split(portfolio)
    if test[TARGET].nunique() < 2:
        raise ValueError(
            "Los Clientes de prueba tienen una sola clase; no se pueden calcular ROC-AUC ni PR-AUC."
        )
    return test


def _metrics(test: pd.DataFrame) -> Metrics:
    y = test[TARGET]
    roc_auc = float(roc_auc_score(y, test["p_churn"]))
    pr_auc = float(average_precision_score(y, test["p_churn"]))
    brier_raw = float(brier_score_loss(y, test["p_raw"]))
    brier_calibrated = float(brier_score_loss(y, test["p_churn"]))
    return {
        "n_test": int(len(test)),
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier_raw": brier_raw,
        "brier_calibrated": brier_calibrated,
        "accepted": is_accepted(roc_auc, pr_auc, brier_raw, brier_calibrated),
    }


def evaluate(portfolio: pd.DataFrame) -> Metrics:
    """Métricas calculadas solo con las filas `split == "test"`."""
    return _metrics(_test_clients(portfolio))


def reliability_figure(test: pd.DataFrame) -> Figure:
    """Curva de fiabilidad de los Clientes de prueba, antes y después de calibrar."""
    fig = Figure(figsize=(6, 6))
    ax = fig.subplots()
    ax.plot([0, 1], [0, 1], "k--", label="Calibración perfecta")
    for column, label in [("p_raw", "Sin calibrar"), ("p_churn", "Calibrada")]:
        observed, predicted = calibration_curve(
            test[TARGET], test[column], n_bins=RELIABILITY_BINS, strategy="quantile"
        )
        ax.plot(predicted, observed, marker="o", label=label)
    ax.set_xlabel("Probabilidad de fuga predicha")
    ax.set_ylabel("Proporción observada de fugas")
    ax.set_title("Curva de fiabilidad (Clientes de prueba)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def run_evaluation(models_dir=MODELS_DIR, reports_dir=REPORTS_DIR) -> Metrics:
    models_dir = Path(models_dir)
    figure_path = reliability_path(reports_dir)
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    portfolio = pd.read_csv(models_dir / "portfolio_scored.csv")
    test = _test_clients(portfolio)
    metrics = _metrics(test)

    with open(models_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    reliability_figure(test).savefig(figure_path, dpi=150)
    return metrics
