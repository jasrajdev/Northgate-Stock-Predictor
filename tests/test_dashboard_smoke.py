"""Starts the Streamlit app headlessly and renders every panel. Skips if local data is absent."""
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not (ROOT / "data/processed/market_panel.csv").exists(), reason="local market data not built")
def test_every_panel_renders_without_exceptions():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=240).run()
    panels = at.sidebar.radio[0].options
    assert len(panels) == 7
    for p in panels:
        at.sidebar.radio[0].set_value(p).run()
        assert not at.exception, (p, [e.value for e in at.exception])
