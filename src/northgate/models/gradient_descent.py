"""Manual batch gradient-descent linear regression (PRD section 7.5, listing 7.1).

Minimises mean squared error L = (1/n) * sum((Xw + b - y)^2) with
w <- w - lr * (2/n) X^T (Xw + b - y) and b <- b - lr * (2/n) sum(Xw + b - y).
Used only to verify the optimisation maths against the closed-form OLS solution.
"""
from __future__ import annotations
import numpy as np


def gd_linreg(X, y, lr: float = 0.1, epochs: int = 5000, tol: float = 1e-14):
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    n, d = X.shape
    w, b, history = np.zeros(d), 0.0, []
    for _ in range(epochs):
        err = X @ w + b - y
        loss = float(np.mean(err ** 2)); history.append(loss)
        w -= lr * (2 / n) * (X.T @ err)
        b -= lr * (2 / n) * err.sum()
        if len(history) > 1 and abs(history[-2] - history[-1]) < tol:
            break
    return w, b, np.array(history)


def ols_closed_form(X, y):
    """Normal-equation solution with an intercept column (least squares)."""
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    A = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    return beta[1:], float(beta[0])
