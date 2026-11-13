import pandas as pd
import pytest

from scripts.merge_cpi_release_events import merge_cpi_events


def sample_events():
    return pd.DataFrame([
        {
            "reference_month": "2025-03",
            "release_workbook_month": "2025-03",
            "base_year": 2012,
            "combined_cpi_index_2012": 192.0,
            "combined_cpi_yoy_inflation_pct": 3.34,
            "actual_release_date": "2025-04-15",
            "available_at_ist": "2025-04-15 16:00:00",
            "next_nse_session": "2025-04-16",
            "timestamp_status": "verified_pdf",
            "provisional": True,
        },
        {
            "reference_month": "2025-04",
            "release_workbook_month": "2025-04",
            "base_year": 2012,
            "combined_cpi_index_2012": 192.6,
            "combined_cpi_yoy_inflation_pct": 3.16,
            "actual_release_date": "2025-05-13",
            "available_at_ist": "2025-05-13 16:00:00",
            "next_nse_session": "2025-05-14",
            "timestamp_status": "verified_official_PIB_and_MoSPI_PDF",
            "provisional": True,
        },
    ])


def test_cpi_is_unavailable_on_release_date_and_available_next_session():
    market = pd.DataFrame({
        "date": ["2025-04-15", "2025-04-16", "2025-05-13", "2025-05-14"],
        "ticker": ["A", "A", "B", "B"],
    })
    result = merge_cpi_events(market, sample_events())

    assert pd.isna(result.loc[0, "release_workbook_month"])
    assert result.loc[1, "release_workbook_month"] == "2025-03"
    assert result.loc[2, "release_workbook_month"] == "2025-03"
    assert result.loc[3, "release_workbook_month"] == "2025-04"
    assert result.loc[3, "combined_cpi_index_2012"] == 192.6


def test_market_rows_and_original_order_are_preserved():
    market = pd.DataFrame({
        "date": ["2025-05-14", "2025-04-15", "2025-04-16"],
        "ticker": ["B", "A", "A"],
        "row_id": [1, 2, 3],
    })
    result = merge_cpi_events(market, sample_events())
    assert result["row_id"].tolist() == [1, 2, 3]
    assert result["ticker"].tolist() == ["B", "A", "A"]


def test_duplicate_cpi_availability_sessions_are_rejected():
    market = pd.DataFrame({"date": ["2025-05-14"]})
    events = pd.concat([sample_events(), sample_events().iloc[[1]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate availability sessions"):
        merge_cpi_events(market, events)
