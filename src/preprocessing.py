"""Carga del dataset, resumen y detección de variables con fuga de datos."""
from pathlib import Path
from typing import TypedDict

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import DATA_PATH, SEED

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


def input_features(
    df: pd.DataFrame, excluded: list[ExcludedFeature] | None = None
) -> list[str]:
    """Columnas de df menos TARGET y las excluidas.

    `excluded` permite reutilizar una lista ya calculada (por ejemplo, sobre la
    partición de entrenamiento) en lugar de recalcular las correlaciones con df.
    """
    if excluded is None:
        excluded = excluded_features(df)
    names = {item["feature"] for item in excluded}
    return [col for col in df.columns if col != TARGET and col not in names]


def split_data(
    df: pd.DataFrame, seed: int = SEED
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Partición 70/15/15 estratificada por TARGET: (entrenamiento, validación, prueba)."""
    train, rest = train_test_split(
        df, test_size=0.30, stratify=df[TARGET], random_state=seed
    )
    val, test = train_test_split(
        rest, test_size=0.50, stratify=rest[TARGET], random_state=seed
    )
    return train, val, test


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    """StandardScaler para las numéricas y OneHotEncoder para las categóricas."""
    categorical = [col for col in features if col in CATEGORICAL]
    numeric = [col for col in features if col not in CATEGORICAL]
    return ColumnTransformer(
        [
            ("num", StandardScaler(), numeric),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical,
            ),
        ]
    )
