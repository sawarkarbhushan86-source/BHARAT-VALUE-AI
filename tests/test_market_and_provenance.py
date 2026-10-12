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

def test_symbol_mapping_and_normalization():
    """Verify symbol normalization handles .NS, .BO, exchange prefixes, and alias lookups."""
    from bharat_value_ai.data.normalization import normalize_symbol
    from bharat_value_ai.data.registry import company_registry

    assert normalize_symbol("ICICIBANK.NS") == "ICICIBANK"
    assert normalize_symbol("cdsl.bo") == "CDSL"
    assert normalize_symbol("NSE:RELIANCE") == "RELIANCE"
    assert normalize_symbol("  HDFCBANK.NS  ") == "HDFCBANK"

    # Alias lookups via master registry
    comp_icici = company_registry.get_company("icici bank")
    assert comp_icici is not None
    assert comp_icici["symbol"] == "ICICIBANK"

    comp_hdfc = company_registry.get_company("hdfc")
    assert comp_hdfc is not None
    assert comp_hdfc["symbol"] == "HDFCBANK"

def test_market_indices_all_four_benchmarks_including_smallcap_100():
    """Verify all 4 benchmark indices are present and Nifty Smallcap 100 refreshes."""
    from bharat_value_ai.services.market_data_service import market_data_service
    indices = market_data_service.get_market_indices(force_refresh=True)

    assert len(indices) == 4
    names = [idx["name"] for idx in indices]
    assert "NIFTY 50" in names
    assert "NIFTY SMALLCAP 100" in names
    assert "NIFTY BANK" in names
    assert "INDIA VIX" in names

    smallcap = next(idx for idx in indices if idx["name"] == "NIFTY SMALLCAP 100")
    assert smallcap["price"] > 0
    assert "data_source" in smallcap
    assert "status" in smallcap

def test_icicibank_canonical_quote_parity():
    """Verify ICICI Bank prices are identical across quote, snapshot, and fair-value."""
    from bharat_value_ai.services.market_data_service import market_data_service
    from bharat_value_ai.services.snapshot_service import SnapshotService
    from bharat_value_ai.analysis.fair_value import fair_value_engine

    q = market_data_service.get_quote("ICICIBANK")
    val = fair_value_engine.evaluate_valuation("ICICIBANK")
    snap = SnapshotService.get_snapshot("ICICIBANK")

    assert q["price"] > 0
    assert q["price"] == val.current_price
    assert q["price"] == snap.current_price
    assert snap.quote["price"] == q["price"]

def test_provider_failure_retains_last_valid_observation():
    """Verify provider failure retains genuine observation with STALE / LAST AVAILABLE status, never zero."""
    from bharat_value_ai.services.market_data_service import CentralMarketDataService
    from bharat_value_ai.data.providers.base import BaseMarketDataProvider
    from bharat_value_ai.data.normalization import QuoteStatus

    class FailingProvider(BaseMarketDataProvider):
        @property
        def provider_name(self):
            return "failing_mock"
        def get_supported_symbols(self):
            return ["CDSL"]
        def get_quote(self, symbol):
            raise ConnectionError("Upstream timeout")
        def get_historical_ohlcv(self, symbol, period="3mo", interval="1d"):
            return []
        def get_market_indices(self):
            return []

    from bharat_value_ai.data.cache import market_cache
    market_cache.invalidate("CDSL")
    failing_service = CentralMarketDataService(primary_provider=FailingProvider())
    quote = failing_service.get_quote("CDSL")


    assert quote["price"] > 0
    assert quote["status"] in [QuoteStatus.LAST_AVAILABLE.value, QuoteStatus.STALE.value]
    assert quote.get("is_stale") is True or quote.get("is_delayed") is True

def test_provider_health_diagnostics():
    """Verify market provider health reporting exposes latency, provider name, and session."""
    from bharat_value_ai.data.market_provider import market_provider
    health = market_provider.get_provider_health()

    assert "status" in health
    assert "provider" in health
    assert "session" in health
    assert "cache" in health
    assert "checked_at_ist" in health

