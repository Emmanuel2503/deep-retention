"""Carga de artefactos y predicción de la Probabilidad de fuga.

keras se importa solo dentro de `ChurnPredictor.load`: la app importa este módulo
para leer la Cartera puntuada (ADR-0002) y no debe cargar TensorFlow por ello.
"""
import json
from pathlib import Path
import os

import joblib
import numpy as np
import pandas as pd

from src.config import MODELS_DIR

EPS = 1e-7

# Columnas de la Cartera puntuada, en orden (contrato de ADR-0002).
PORTFOLIO_DATA_COLUMNS = [
    "CustomerId",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Satisfaction Score",
    "Card Type",
    "Point Earned",
    "Exited",
]
PORTFOLIO_COLUMNS = [*PORTFOLIO_DATA_COLUMNS, "split", "p_raw", "p_churn"]


def logit(p) -> np.ndarray:
    """Logit de la salida de la red, como columna (entrada del calibrador Platt)."""
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p)).reshape(-1, 1)


def apply_calibrator(calibrator, p_raw) -> np.ndarray:
    return calibrator.predict_proba(logit(p_raw))[:, 1]


class ChurnPredictor:
    def __init__(self, model, preprocessor, calibrator, features, categories):
        self.model = model
        self.preprocessor = preprocessor
        self.calibrator = calibrator
        self.features: list[str] = features
        self.categories: dict[str, list[str]] = categories

    @classmethod
    def load(cls, models_dir: Path = MODELS_DIR) -> "ChurnPredictor":
        import keras

        models_dir = Path(models_dir)
        with open(models_dir / "features.json", encoding="utf-8") as f:
            meta = json.load(f)
        return cls(
            model=keras.models.load_model(models_dir / "model.keras"),
            preprocessor=joblib.load(models_dir / "preprocessor.joblib"),
            calibrator=joblib.load(models_dir / "calibrator.joblib"),
            features=meta["features"],
            categories=meta["categories"],
        )

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        return self.preprocessor.transform(df[self.features])

    def _raw_from_transformed(self, X: np.ndarray) -> np.ndarray:
        return np.asarray(self.model.predict(X, batch_size=1024, verbose=0)).ravel()

    def predict_raw(self, df: pd.DataFrame) -> np.ndarray:
        return self._raw_from_transformed(self.transform(df))

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        return apply_calibrator(self.calibrator, self.predict_raw(df))

    def predict_transformed(self, X: np.ndarray) -> np.ndarray:
        return apply_calibrator(self.calibrator, self._raw_from_transformed(X))

def load_portfolio(path: Path | None = None) -> pd.DataFrame: 
    if path is None: 
        env_path = os.getenv("DEEP_RETENTION_PORTFOLIO") 
        if env_path: 
            path = Path(env_path) 
        else: 
            path = Path(MODELS_DIR) / "portfolio_scored.csv" 
        if not path.exists(): 
            path = Path("data/fixtures/portfolio_cases.csv") 
            
    return pd.read_csv(path)