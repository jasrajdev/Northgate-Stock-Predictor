"""Financial mathematics implemented from first principles (PRD section 7, 11).

Conventions: daily simple returns; 252 sessions a year; risk-free rate and costs from
config/recommendation.json. Covariance shrinkage uses Ledoit-Wolf (scikit-learn).
Optimisation is long-only, fully invested, with a per-asset cap, solved by SLSQP.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize

TD = 252


# ---------- returns and single-series metrics ----------
def simple_returns(prices: pd.DataFrame | pd.Series):
    return prices.pct_change(fill_method=None)


def log_returns(prices):
    return np.log(prices / prices.shift(1))


def annualise_mean(r: pd.Series) -> float:
    return float(r.mean() * TD)


def annualise_vol(r: pd.Series) -> float:
    return float(r.std(ddof=1) * np.sqrt(TD))


def cagr(r: pd.Series) -> float:
    r = r.dropna()
    return float((1 + r).prod() ** (TD / len(r)) - 1) if len(r) else np.nan


def sharpe(r: pd.Series, rf_annual: float) -> float:
    ex = r.dropna() - rf_annual / TD
    return float(ex.mean() / ex.std(ddof=1) * np.sqrt(TD))


def sortino(r: pd.Series, rf_annual: float) -> float:
    ex = r.dropna() - rf_annual / TD
    downside = np.sqrt((np.minimum(ex, 0) ** 2).mean())
    return float(ex.mean() / downside * np.sqrt(TD)) if downside > 0 else np.nan


def drawdown(r: pd.Series) -> pd.Series:
    v = (1 + r.fillna(0)).cumprod()
    return v / v.cummax() - 1


def max_drawdown(r: pd.Series) -> float:
    return float(drawdown(r).min())


def calmar(r: pd.Series) -> float:
    mdd = max_drawdown(r)
    return float(cagr(r) / abs(mdd)) if mdd < 0 else np.nan


def var_historical(r: pd.Series, level: float = 0.95) -> float:
    """Historical one-day Value at Risk as a (negative) return quantile."""
    return float(r.dropna().quantile(1 - level))


def beta(r: pd.Series, m: pd.Series) -> float:
    both = pd.concat([r, m], axis=1).dropna()
    return float(np.cov(both.iloc[:, 0], both.iloc[:, 1], ddof=1)[0, 1] / np.var(both.iloc[:, 1], ddof=1))


def covariance(r: pd.DataFrame) -> pd.DataFrame:
    """Sample covariance from first principles: E[(x-mu)(y-mu)] with n-1."""
    x = r.dropna().to_numpy(); x = x - x.mean(axis=0)
    return pd.DataFrame(x.T @ x / (len(x) - 1), index=r.columns, columns=r.columns)


def ledoit_wolf(r: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    from sklearn.covariance import LedoitWolf
    lw = LedoitWolf().fit(r.dropna().to_numpy())
    return pd.DataFrame(lw.covariance_, index=r.columns, columns=r.columns), float(lw.shrinkage_)


def summary(r: pd.Series, rf_annual: float, market: pd.Series | None = None) -> dict:
    r = r.dropna()
    return {"Total return": float((1 + r).prod() - 1), "CAGR": cagr(r), "Volatility": annualise_vol(r),
            "Sharpe": sharpe(r, rf_annual), "Sortino": sortino(r, rf_annual), "Max drawdown": max_drawdown(r),
            "Calmar": calmar(r), "VaR 95% (1-day)": var_historical(r), "Beta": beta(r, market) if market is not None else np.nan}


# ---------- portfolio optimisation ----------
def _bounds(n, cap):
    return [(0.0, cap)] * n


def _cons(extra=None):
    c = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    return c + (extra or [])


def min_variance(cov: pd.DataFrame, cap: float = 1.0) -> pd.Series:
    n, S = len(cov), cov.to_numpy()
    res = minimize(lambda w: w @ S @ w, np.full(n, 1 / n), method="SLSQP", bounds=_bounds(n, cap), constraints=_cons(),
                   options={"maxiter": 500, "ftol": 1e-12})
    return pd.Series(np.clip(res.x, 0, None) / np.clip(res.x, 0, None).sum(), index=cov.index)


def max_sharpe(mu: pd.Series, cov: pd.DataFrame, rf: float, cap: float = 1.0) -> pd.Series:
    n, S, m = len(cov), cov.to_numpy(), mu.to_numpy()
    neg = lambda w: -((w @ m - rf) / np.sqrt(w @ S @ w))
    res = minimize(neg, np.full(n, 1 / n), method="SLSQP", bounds=_bounds(n, cap), constraints=_cons(), options={"maxiter": 500, "ftol": 1e-12})
    w = np.clip(res.x, 0, None)
    return pd.Series(w / w.sum(), index=cov.index)


def target_return(mu: pd.Series, cov: pd.DataFrame, target: float, cap: float = 1.0) -> pd.Series | None:
    n, S, m = len(cov), cov.to_numpy(), mu.to_numpy()
    res = minimize(lambda w: w @ S @ w, np.full(n, 1 / n), method="SLSQP", bounds=_bounds(n, cap),
                   constraints=_cons([{"type": "eq", "fun": lambda w: w @ m - target}]), options={"maxiter": 500, "ftol": 1e-12})
    return pd.Series(res.x, index=cov.index) if res.success else None


def perf(w: pd.Series, mu: pd.Series, cov: pd.DataFrame, rf: float) -> tuple[float, float, float]:
    ret, vol = float(w @ mu), float(np.sqrt(w @ cov @ w))
    return ret, vol, (ret - rf) / vol


def efficient_frontier(mu, cov, cap=1.0, points=30) -> pd.DataFrame:
    lo = float(min_variance(cov, cap) @ mu)
    hi = float(np.sort(mu.to_numpy())[::-1][: int(np.ceil(1 / cap))].mean()) if cap < 1 else float(mu.max())
    rows = []
    for t in np.linspace(lo, hi, points):
        w = target_return(mu, cov, t, cap)
        if w is not None:
            rows.append({"return": float(w @ mu), "volatility": float(np.sqrt(w @ cov @ w))})
    return pd.DataFrame(rows)


def monte_carlo(mu, cov, rf, n=20000, seed=42) -> pd.DataFrame:
    """Random long-only portfolios (Dirichlet weights) to cross-check the optimiser."""
    w = np.random.default_rng(seed).dirichlet(np.ones(len(mu)), n)
    ret = w @ mu.to_numpy(); vol = np.sqrt(np.einsum("ij,jk,ik->i", w, cov.to_numpy(), w))
    return pd.DataFrame({"return": ret, "volatility": vol, "sharpe": (ret - rf) / vol, "max_weight": w.max(axis=1)})


# ---------- backtest ----------
def backtest(rets: pd.DataFrame, start, end, strategy: str, rf: float, cap: float, lookback: int, every: int,
             cost_bps: float) -> tuple[pd.Series, pd.DataFrame, float]:
    """Walk-forward rebalanced portfolio. Weights at each rebalance use only returns BEFORE that date.
    Returns (daily net returns, weight history, total one-way turnover)."""
    dates = rets.index[(rets.index >= pd.Timestamp(start)) & (rets.index <= pd.Timestamp(end))]
    n = rets.shape[1]; w = pd.Series(0.0, index=rets.columns); out, hist, turnover = [], [], 0.0
    for i, d in enumerate(dates):
        if i % every == 0:
            past = rets.loc[rets.index < d].tail(lookback).dropna()
            if strategy == "equal_weight":
                target = pd.Series(1 / n, index=rets.columns)
            else:
                cov, _ = ledoit_wolf(past)
                cov, mu = cov * TD, past.mean() * TD
                target = min_variance(cov, cap) if strategy == "min_variance" else max_sharpe(mu, cov, rf, cap)
            trade = float((target - w).abs().sum()); turnover += trade
            cost = trade * cost_bps / 1e4; w = target; hist.append({"date": d, **w.to_dict()})
        else:
            cost = 0.0
        r = float((w * rets.loc[d].fillna(0)).sum()) - cost
        out.append(r)
        w = w * (1 + rets.loc[d].fillna(0)); w = w / w.sum()  # drift
    return pd.Series(out, index=dates), pd.DataFrame(hist).set_index("date"), turnover
