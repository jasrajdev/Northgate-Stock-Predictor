"""Unit tests for finance maths, features, recommendations, sentiment timing and model loading.
None of these tests reads the held-out test partition."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from northgate import config, finance as FN, features as F, recommend as R, sentiment as S

ROOT = Path(__file__).resolve().parents[1]
CFG = config.recommendation()


def rand_returns(n=600, k=5, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame(rng.normal(0.0004, 0.012, (n, k)) + rng.normal(0, 0.006, (n, 1)), index=idx, columns=list("ABCDE"))


# ---------- finance ----------
def test_covariance_matches_numpy():
    r = rand_returns()
    assert np.allclose(FN.covariance(r).to_numpy(), np.cov(r.to_numpy().T, ddof=1))


def test_sharpe_sortino_drawdown_var_by_hand():
    r = pd.Series([0.01, -0.02, 0.015, -0.005, 0.02, -0.03, 0.01])
    ex = r - 0.05 / 252
    assert FN.sharpe(r, 0.05) == pytest.approx(ex.mean() / ex.std(ddof=1) * np.sqrt(252))
    dn = np.sqrt((np.minimum(ex, 0) ** 2).mean())
    assert FN.sortino(r, 0.05) == pytest.approx(ex.mean() / dn * np.sqrt(252))
    v = (1 + r).cumprod(); assert FN.max_drawdown(r) == pytest.approx((v / v.cummax() - 1).min())
    assert FN.var_historical(r, 0.95) == pytest.approx(r.quantile(0.05))
    m = pd.Series([0.005, -0.01, 0.01, 0.0, 0.01, -0.02, 0.004])
    assert FN.beta(r, m) == pytest.approx(np.cov(r, m, ddof=1)[0, 1] / np.var(m, ddof=1))


def test_optimisers_respect_constraints_and_beat_equal_weight():
    r = rand_returns(); cov, s = FN.ledoit_wolf(r); cov *= 252; mu = r.mean() * 252
    assert 0 <= s <= 1 and np.all(np.linalg.eigvalsh(cov.to_numpy()) > 0)
    for w in (FN.min_variance(cov, 0.3), FN.max_sharpe(mu, cov, 0.05, 0.3)):
        assert w.sum() == pytest.approx(1, abs=1e-6) and w.min() >= -1e-9 and w.max() <= 0.3 + 1e-6
    ew = pd.Series(0.2, index=mu.index)
    assert FN.perf(FN.max_sharpe(mu, cov, 0.05, 0.3), mu, cov, 0.05)[2] >= FN.perf(ew, mu, cov, 0.05)[2] - 1e-6
    assert FN.perf(FN.min_variance(cov, 0.3), mu, cov, 0.05)[1] <= FN.perf(ew, mu, cov, 0.05)[1] + 1e-9
    mc = FN.monte_carlo(mu, cov, 0.05, n=2000)
    assert len(mc) == 2000 and mc.sharpe.max() <= FN.perf(FN.max_sharpe(mu, cov, 0.05, 1.0), mu, cov, 0.05)[2] + 1e-6


def test_backtest_uses_only_past_data():
    r = rand_returns(); start = r.index[520]
    ret, w, _ = FN.backtest(r, start, r.index[-1], "min_variance", 0.05, 0.3, 504, 63, 10)
    r2 = r.copy(); r2.loc[r2.index > start] *= 5  # future shock must not change the first rebalance
    _, w2, _ = FN.backtest(r2, start, r.index[-1], "min_variance", 0.05, 0.3, 504, 63, 10)
    assert np.allclose(w.iloc[0], w2.iloc[0])


# ---------- features ----------
def toy_panel(n=300):
    d = pd.bdate_range("2022-01-03", periods=n); rng = np.random.default_rng(1)
    px = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    return pd.DataFrame({"Date": d, "Ticker": "AAA.NS", "Name": "A", "Open": px, "High": px * 1.01, "Low": px * 0.99,
                         "Close": px, "Adj Close": px, "Volume": rng.integers(1e5, 1e6, n)})


def test_features_are_backward_looking():
    p = toy_panel(); full = F.build(p).set_index("Date")
    cut = p.Date.iloc[220]; part = F.build(p[p.Date <= cut]).set_index("Date")
    a, b = full.loc[part.index, F.FEATURES].astype(float), part[F.FEATURES].astype(float)
    assert ((a - b).abs().fillna(0) < 1e-12).all().all() and (a.isna() == b.isna()).all().all()
    assert len(F.FEATURES) == 25


def test_labels_masked_after_validation_and_test_partition_not_offered():
    p = toy_panel(); p["Date"] = pd.bdate_range("2026-01-01", periods=len(p))
    lab = F.add_labels(F.build(p))
    assert lab.loc[lab.Date >= config.VALIDATION_TARGET_END, F.TARGET].isna().all()
    with pytest.raises(ValueError):
        F.partition(lab, "test")


# ---------- recommendations ----------
def _decide(forecasts, weights, edge, sentiment=None, cfg=None):
    t = list(forecasts); vol = pd.Series(0.015, index=t)
    return {d.ticker: d for d in R.decide(t, forecasts, vol, sentiment or {}, pd.Series(weights), cfg or CFG, edge)}


def test_no_validated_edge_means_no_action():
    d = _decide({"A": 0.05, "B": -0.05}, {"A": 0.1, "B": 0.1}, edge=False)
    assert {x.action for x in d.values()} == {"HOLD"}
    assert R.portfolio_action(list(d.values())) == "No action recommended"


def test_buy_sell_reduce_rules():
    cfg = dict(CFG, require_validated_edge=False)
    d = _decide({"A": 0.05, "B": -0.05, "C": 0.0}, {"A": 0.1, "B": 0.1, "C": 0.5}, edge=False, cfg=cfg)
    assert d["A"].action == "BUY" and d["B"].action == "SELL" and d["C"].action == "REDUCE"
    d = _decide({"A": -0.05}, {"A": 0.0}, edge=True)  # cannot sell what is not held
    assert d["A"].action == "HOLD"


def test_risk_alone_never_triggers_sale():
    t = ["A", "B", "C"]; vol = pd.Series([0.01, 0.01, 0.06], index=t)
    d = R.decide(t, {"A": 0.0, "B": 0.0, "C": 0.0}, vol, {}, pd.Series(0.2, index=t), CFG, True)
    assert all(x.action == "HOLD" for x in d)


# ---------- sentiment timing ----------
def test_after_close_and_weekend_news_map_to_next_session():
    sessions = pd.DatetimeIndex(["2025-03-14", "2025-03-17", "2025-03-18"])
    ts = pd.Series(["2025-03-17T09:00:00Z",   # 14:30 IST, during session -> same day
                    "2025-03-17T10:00:00Z",   # 15:30 IST, at close -> next session
                    "2025-03-15T05:00:00Z",   # Saturday -> Monday
                    "2025-03-14T18:45:00Z"])  # 00:15 IST Saturday -> Monday
    out = S.first_available_session(ts, sessions).session.dt.strftime("%Y-%m-%d").tolist()
    assert out == ["2025-03-17", "2025-03-18", "2025-03-17", "2025-03-17"]


# ---------- models ----------
def test_deep_checkpoint_roundtrip(tmp_path):
    torch = pytest.importorskip("torch")
    from northgate.models import deep
    feats, tickers, seq, hidden = F.FEATURES, ["AAA.NS", "BBB.NS"], 30, 24
    for kind in ("LSTM", "GRU", "BiLSTM", "Transformer"):
        m = deep.build(kind, len(feats) + len(tickers), hidden, seq)
        ck = {"state_dict": m.state_dict(), "model": kind, "sequence_length": seq, "hidden_size": hidden,
              "ticker_map": {t: i for i, t in enumerate(tickers)}, "feature_columns": feats,
              "medians": {f: 0.0 for f in feats}, "means": {f: 0.0 for f in feats}, "stds": {f: 1.0 for f in feats}}
        p = tmp_path / f"{kind.lower()}_best.pt"; torch.save(ck, p)
        loaded = deep.load(p, expected_features=feats)
        frame = F.build(toy_panel()).assign(Ticker="AAA.NS")
        assert np.isfinite(loaded.predict(frame, "AAA.NS")) and loaded.window(frame, "AAA.NS").shape == (seq, len(feats) + 2)
        with pytest.raises(ValueError):
            deep.load(p, expected_features=list(reversed(feats)))


def test_persisted_classical_models_predict():
    from northgate.models import CLASSICAL, classical
    meta = classical.metadata()
    if not meta:
        pytest.skip("run scripts/persist_classical_models.py first")
    assert meta["test_partition_read"] is False and meta["features"] == F.FEATURES
    X = F.build(toy_panel()).tail(3)
    for name in CLASSICAL:
        assert np.isfinite(classical.predict(name, meta["tickers"][0], X)).all()


def test_no_source_file_reads_test_split():
    offenders = [p for p in (ROOT / "src").rglob("*.py") if "test.csv" in p.read_text()]
    offenders += [p for p in (ROOT / "dashboard").rglob("*.py") if "test.csv" in p.read_text()]
    assert not offenders, offenders
