"""Unit tests for Zerodha Kite Connect Market Provider, Rate Limiting, and Resilience."""
import pytest
import time
from unittest.mock import patch, MagicMock
from bharat_value_ai.data.providers.kite_provider import (
    ZerodhaKiteMarketProvider,
    KiteRateLimiter,
    KiteCircuitBreaker,
    KiteWebSocketManager,
)


def test_kite_rate_limiter():
    """Verify rate limiter enforces max calls per interval."""
    limiter = KiteRateLimiter(max_per_second=10.0)  # 0.1s interval
    start = time.time()
    for _ in range(3):
        limiter.wait()
    elapsed = time.time() - start
    assert elapsed >= 0.18  # throttled over 2 intervals


def test_kite_circuit_breaker_state_transitions():
    """Verify circuit breaker opens after consecutive failures and recovers on success."""
    cb = KiteCircuitBreaker(failure_threshold=3, recovery_timeout_seconds=0.5)
    assert cb.can_attempt() is True
    assert cb.is_open is False

    cb.record_failure()
    cb.record_failure()
    assert cb.can_attempt() is True

    cb.record_failure()  # 3rd failure trips breaker
    assert cb.is_open is True
    assert cb.can_attempt() is False

    # Force recovery timeout expiration
    cb.last_failure_time = time.time() - 1.0
    assert cb.can_attempt() is True  # enters half-open recovery

    cb.record_success()
    assert cb.is_open is False
    assert cb.failure_count == 0


def test_kite_provider_unconfigured():
    """When credentials are not configured, provider returns informative health status without crashing."""
    provider = ZerodhaKiteMarketProvider(api_key="", access_token="")
    health = provider.check_health()
    assert health["provider"] == "Zerodha Kite Connect v3"
    assert health["status"] == "NOT_CONFIGURED"
    assert "Credentials not set" in health["message"] or "not set" in health["message"]
    # Quotes return None when unconfigured
    quote = provider.get_quote("RELIANCE")
    assert quote is None


def test_kite_provider_mock_quote_success():
    """Verify Kite quote parser converts Kite Connect v3 response to canonical quote schema."""
    provider = ZerodhaKiteMarketProvider(api_key="mock_key", access_token="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "NSE:RELIANCE": {
                "instrument_token": 738561,
                "timestamp": "2026-10-12 15:30:00",
                "last_price": 2980.50,
                "net_change": 25.50,
                "ohlc": {
                    "open": 2960.0,
                    "high": 2995.0,
                    "low": 2955.0,
                    "close": 2955.0,
                },
                "volume": 4520100,
                "depth": {
                    "buy": [{"quantity": 100, "price": 2980.0}],
                    "sell": [{"quantity": 200, "price": 2980.50}],
                },
            }
        },
    }

    with patch.object(provider.session, "get", return_value=mock_resp):
        quote = provider.get_quote("RELIANCE")
        assert quote is not None
        assert quote["symbol"] == "RELIANCE"
        assert quote["price"] == 2980.50
        assert quote["change"] == 25.50
        assert quote["open_price"] == 2960.0
        assert quote["high_price"] == 2995.0
        assert quote["low_price"] == 2955.0
        assert quote["volume"] == 4520100
        assert quote["data_source"] == "zerodha_kite_connect_v3"
        assert quote["status"] == "LIVE"


def test_kite_provider_unauthorized_error():
    """Verify 403 Forbidden logs error, records circuit breaker failure, and returns None."""
    provider = ZerodhaKiteMarketProvider(api_key="bad_key", access_token="bad_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "TokenException: Token is invalid or has expired."

    with patch.object(provider.session, "get", return_value=mock_resp):
        quote = provider.get_quote("RELIANCE")
        assert quote is None
        assert provider.circuit_breaker.failure_count == 1


def test_kite_provider_rate_limited_error():
    """Verify 429 Too Many Requests logs warning, increments circuit breaker, and returns None."""
    provider = ZerodhaKiteMarketProvider(api_key="mock_key", access_token="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Too many requests. Limit: 3 requests per second."

    with patch.object(provider.session, "get", return_value=mock_resp):
        quote = provider.get_quote("TCS")
        assert quote is None
        assert provider.circuit_breaker.failure_count == 1


def test_kite_provider_timeout_opens_circuit_breaker():
    """Verify network timeouts trigger circuit breaker failures."""
    provider = ZerodhaKiteMarketProvider(api_key="mock_key", access_token="mock_token")

    import requests
    with patch.object(provider.session, "get", side_effect=requests.exceptions.Timeout("Connection timed out")):
        quote = provider.get_quote("INFY")
        assert quote is None
        assert provider.circuit_breaker.failure_count == 1


def test_kite_provider_historical_candles_parsing():
    """Verify historical candles are parsed into canonical OHLCV dictionary list."""
    provider = ZerodhaKiteMarketProvider(api_key="mock_key", access_token="mock_token")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {
            "candles": [
                ["2026-10-08T09:15:00+0530", 2950.0, 2975.0, 2945.0, 2970.0, 120000],
                ["2026-10-09T09:15:00+0530", 2970.0, 2990.0, 2965.0, 2985.0, 140000],
            ]
        },
    }

    with patch.object(provider.session, "get", return_value=mock_resp):
        candles = provider.get_historical_ohlcv("RELIANCE", period="1mo", interval="1d")
        assert len(candles) == 2
        assert candles[0]["open"] == 2950.0
        assert candles[0]["high"] == 2975.0
        assert candles[0]["low"] == 2945.0
        assert candles[0]["close"] == 2970.0
        assert candles[0]["volume"] == 120000
        assert candles[0]["symbol"] == "RELIANCE"


def test_kite_websocket_manager_config_and_tokens():
    """Verify Kite WebSocket manager tracks token subscriptions and connection URLs."""
    mgr = KiteWebSocketManager(api_key="test_key", access_token="test_token")
    assert mgr.is_configured() is True
    assert "test_key" in mgr.get_connection_url()
    assert "test_token" in mgr.get_connection_url()

    mgr.subscribe_tokens([738561, 2953217])
    status = mgr.get_stream_status()
    assert status["configured"] is True
    assert status["subscribed_tokens_count"] == 2
    assert status["protocol"] == "KiteTicker-v3-Binary"
