"""Arquitectura de la red, entrenamiento y calibración Platt."""
from dataclasses import dataclass

import keras
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_class_weight

from src.inference import logit

PATIENCE = 12


@dataclass
class TrainOutcome:
    history: keras.callbacks.History
    stopped_epoch: int
    best_epoch: int


def build_model(n_inputs: int) -> keras.Model:
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(n_inputs,)),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
    )
    return model


def train_model(
    model, X_tr, y_tr, X_val, y_val, *, epochs=200, patience=PATIENCE, batch_size=64
) -> TrainOutcome:
    """Entrena con class_weight balanceado y EarlyStopping sobre val_loss.

    Las épocas se numeran desde 0 (como el historial): `best_epoch` es el índice
    de la menor val_loss y `stopped_epoch` el de la última época ejecutada.
    """
    y_tr = np.asarray(y_tr)
    classes = np.unique(y_tr)
    weights = compute_class_weight("balanced", classes=classes, y=y_tr)
    class_weight = {int(c): float(w) for c, w in zip(classes, weights)}
    early_stopping = keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=patience, restore_best_weights=True
    )
    history = model.fit(
        X_tr,
        y_tr,
        validation_data=(X_val, np.asarray(y_val)),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=[early_stopping],
        verbose=2,
    )
    val_loss = history.history["val_loss"]
    return TrainOutcome(
        history=history,
        stopped_epoch=len(val_loss) - 1,
        best_epoch=int(np.argmin(val_loss)),
    )


def fit_calibrator(p_raw_val: np.ndarray, y_val: np.ndarray) -> LogisticRegression:
    """Calibración Platt: regresión logística sobre el logit de la salida de la red."""
    calibrator = LogisticRegression(C=1e6)
    calibrator.fit(logit(p_raw_val), np.asarray(y_val))
    return calibrator
