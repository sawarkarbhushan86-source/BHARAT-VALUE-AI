"""Unit tests for Indian Market Data Providers and Point-in-Time Provenance."""
from datetime import datetime, timezone, timedelta
from bharat_value_ai.core.provenance import PointInTimeEngine
from bharat_value_ai.data.market_provider import market_provider, is_indian_market_open

def test_indian_market_open_logic():
    res = is_indian_market_open()
    assert "is_open" in res
    assert "reason" in res
    assert "current_ist" in res

def test_candle_quality_diagnostics_valid():
    # Valid candle: High is max, Low is min, positive price and volume
    diags = PointInTimeEngine.validate_ohlcv_candle(
        open_p=100.0, high_p=110.0, low_p=95.0, close_p=105.0, volume=50000
    )
    assert len(diags) == 0

def test_candle_quality_diagnostics_impossible_high():
    # Impossible candle: High is lower than close
    diags = PointInTimeEngine.validate_ohlcv_candle(
        open_p=100.0, high_p=102.0, low_p=95.0, close_p=105.0, volume=50000
    )
    assert any(d.check_name == "OHLC_HIGH_VIOLATION" for d in diags)

def test_candle_quality_diagnostics_negative_price():
    diags = PointInTimeEngine.validate_ohlcv_candle(
        open_p=-10.0, high_p=10.0, low_p=-15.0, close_p=5.0, volume=100
    )
    assert any(d.check_name == "NEGATIVE_PRICE_VIOLATION" for d in diags)

def test_point_in_time_financials_filtering():
    as_of = datetime(2023, 10, 1, tzinfo=timezone.utc)
    records = [
        {"period": "FY22", "public_availability_date": datetime(2022, 6, 1, tzinfo=timezone.utc)},
        {"period": "FY23", "public_availability_date": datetime(2023, 6, 1, tzinfo=timezone.utc)},
        {"period": "FY24", "public_availability_date": datetime(2024, 6, 1, tzinfo=timezone.utc)} # Future result!
    ]
    filtered = PointInTimeEngine.filter_point_in_time_financials(records, as_of)
    assert len(filtered) == 2
    assert all(r["period"] != "FY24" for r in filtered)

def test_market_provider_quote():
    quote = market_provider.get_quote("CDSL")
    assert quote["symbol"] == "CDSL"
    assert quote["price"] > 0
    assert quote["exchange"] == "NSE"
    assert "data_source" in quote
