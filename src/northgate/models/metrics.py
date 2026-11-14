"""Metric definitions identical to the Experiment-01 walk-forward runner."""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred, current, direction_pred=None) -> dict:
    y_true, y_pred, current = (np.asarray(a, dtype=float) for a in (y_true, y_pred, current))
    actual, predicted = current * np.exp(y_true), current * np.exp(y_pred)
    direction = y_pred if direction_pred is None else np.asarray(direction_pred, dtype=float)
    return {"mae": float(mean_absolute_error(actual, predicted)),
            "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
            "mape_pct": float(np.mean(np.abs((actual - predicted) / np.maximum(np.abs(actual), 1e-12))) * 100),
            "r2": float(r2_score(actual, predicted)),
            "directional_accuracy": float(np.mean(np.sign(y_true) == np.sign(direction)))}
