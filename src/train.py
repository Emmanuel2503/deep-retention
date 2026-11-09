"""Orquesta el entrenamiento completo y exporta los artefactos (ADR-0001, ADR-0002)."""
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import keras
import tensorflow as tf

from src.config import DATA_PATH, MODELS_DIR, SEED
from src.inference import PORTFOLIO_COLUMNS, PORTFOLIO_DATA_COLUMNS, apply_calibrator
from src.model import build_model, fit_calibrator, train_model
from src.preprocessing import (
    CATEGORICAL,
    TARGET,
    build_preprocessor,
    excluded_features,
    input_features,
    load_dataset,
    split_data,
)


@dataclass
class TrainingResult:
    split_ids: dict[str, list[int]]
    stopped_epoch: int
    best_epoch: int
    val_loss: list[float]  # val_loss por época del historial (índice = época)


def fitted_categories(preprocessor, features: list[str]) -> dict[str, list[str]]:
    """Categorías que aprendió el OneHotEncoder con la partición de entrenamiento."""
    categorical = [col for col in features if col in CATEGORICAL]
    if not categorical:
        return {}
    encoder = preprocessor.named_transformers_["cat"]
    return {
        col: [str(value) for value in values]
        for col, values in zip(categorical, encoder.categories_)
    }


def run_training(data_path=DATA_PATH, out_dir=MODELS_DIR, seed=SEED) -> TrainingResult:
    keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()  # reproducible también en GPU
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset(data_path)
    missing = [col for col in PORTFOLIO_DATA_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Al dataset le faltan columnas de la Cartera puntuada: {missing}")

    train, val, test = split_data(df, seed)
    # La detección de fuga usa solo el entrenamiento: val y test no influyen en las entradas.
    excluded = excluded_features(train)
    features = input_features(train, excluded)
    outside = [col for col in features if col not in PORTFOLIO_DATA_COLUMNS]
    if outside:
        raise ValueError(f"Variables de entrada fuera del contrato de ADR-0002: {outside}")

    preprocessor = build_preprocessor(features)
    X_tr = preprocessor.fit_transform(train[features])
    X_val = preprocessor.transform(val[features])

    model = build_model(X_tr.shape[1])
    outcome = train_model(model, X_tr, train[TARGET], X_val, val[TARGET])

    portfolio = df[PORTFOLIO_DATA_COLUMNS].copy()
    portfolio["split"] = "train"
    portfolio.loc[val.index, "split"] = "val"
    portfolio.loc[test.index, "split"] = "test"
    portfolio["p_raw"] = model.predict(
        preprocessor.transform(df[features]), batch_size=1024, verbose=0
    ).ravel()
    calibrator = fit_calibrator(portfolio.loc[val.index, "p_raw"], val[TARGET])
    portfolio["p_churn"] = apply_calibrator(calibrator, portfolio["p_raw"])

    model.save(out_dir / "model.keras")
    joblib.dump(preprocessor, out_dir / "preprocessor.joblib")
    joblib.dump(calibrator, out_dir / "calibrator.joblib")
    meta = {
        "features": features,
        "excluded": excluded,
        "categories": fitted_categories(preprocessor, features),
    }
    with open(out_dir / "features.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    portfolio[PORTFOLIO_COLUMNS].to_csv(out_dir / "portfolio_scored.csv", index=False)

    return TrainingResult(
        split_ids={
            "train": train["CustomerId"].astype(int).tolist(),
            "val": val["CustomerId"].astype(int).tolist(),
            "test": test["CustomerId"].astype(int).tolist(),
        },
        stopped_epoch=outcome.stopped_epoch,
        best_epoch=outcome.best_epoch,
        val_loss=[float(v) for v in outcome.history.history["val_loss"]],
    )


if __name__ == "__main__":
    result = run_training()
    print(
        f"Entrenamiento terminado: mejor época {result.best_epoch}, "
        f"detenido en la época {result.stopped_epoch}."
    )
