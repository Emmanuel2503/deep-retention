"""Carga del dataset, resumen y detección de variables con fuga de datos."""
from pathlib import Path
from typing import TypedDict

import pandas as pd

from src.config import DATA_PATH

TARGET = "Exited"
ID_COLUMNS = ["RowNumber", "CustomerId", "Surname"]
KNOWN_LEAKY = ["Complain"]
CATEGORICAL = ["Geography", "Gender", "Card Type"]
LEAK_THRESHOLD = 0.5

REASON_ID = "identificador"
REASON_LEAK = "fuga de datos"


class ExcludedFeature(TypedDict):
    feature: str
    reason: str
    correlation: float | None


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en {path}. "
            "Coloca Customer-Churn-Records.csv en la carpeta data/ del repositorio."
        )
    return pd.read_csv(path, encoding="utf-8")


def dataset_summary(df: pd.DataFrame) -> dict:
    return {"n_customers": int(len(df)), "churn_rate": float(df[TARGET].mean())}


def feature_correlations(df: pd.DataFrame) -> dict[str, float]:
    """|corr| con TARGET por variable original.

    Las numéricas se correlacionan directamente; las categóricas usan el máximo
    valor absoluto de la correlación de sus columnas one-hot.
    """
    target = df[TARGET]
    result: dict[str, float] = {}
    for col in df.columns:
        if col == TARGET:
            continue
        if col in CATEGORICAL:
            dummies = pd.get_dummies(df[col]).astype(float)
            corr = dummies.corrwith(target).abs().fillna(0.0)
            result[col] = float(corr.max())
        elif pd.api.types.is_numeric_dtype(df[col]):
            value = abs(df[col].corr(target))
            result[col] = 0.0 if pd.isna(value) else float(value)
    return result


def _leaky_columns(correlations: dict[str, float], threshold: float) -> list[str]:
    return [
        col
        for col, corr in correlations.items()
        if col not in ID_COLUMNS and corr > threshold
    ]


def find_leaky_features(
    df: pd.DataFrame, threshold: float = LEAK_THRESHOLD
) -> list[ExcludedFeature]:
    correlations = feature_correlations(df)
    return [
        {"feature": col, "reason": REASON_LEAK, "correlation": correlations[col]}
        for col in _leaky_columns(correlations, threshold)
    ]


def excluded_features(df: pd.DataFrame) -> list[ExcludedFeature]:
    correlations = feature_correlations(df)
    ids = [col for col in ID_COLUMNS if col in df.columns]
    leaky = [col for col in KNOWN_LEAKY if col in df.columns]
    leaky += [
        col for col in _leaky_columns(correlations, LEAK_THRESHOLD) if col not in leaky
    ]
    return [
        ExcludedFeature(feature=col, reason=REASON_ID, correlation=None) for col in ids
    ] + [
        ExcludedFeature(feature=col, reason=REASON_LEAK, correlation=correlations.get(col))
        for col in leaky
    ]


def input_features(df: pd.DataFrame) -> list[str]:
    excluded = {item["feature"] for item in excluded_features(df)}
    return [col for col in df.columns if col != TARGET and col not in excluded]
