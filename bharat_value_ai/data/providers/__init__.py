"""Data providers package with multi-adapter factory."""
import logging
from typing import Optional
from bharat_value_ai.config import settings
from bharat_value_ai.data.providers.base import BaseMarketDataProvider
from bharat_value_ai.data.providers.yfinance_provider import YahooFinanceIndianProvider
from bharat_value_ai.data.providers.kite_provider import ZerodhaKiteMarketProvider

logger = logging.getLogger(__name__)

def get_market_provider(provider_name: Optional[str] = None) -> BaseMarketDataProvider:
    """
    Factory returning configured market data provider adapter.
    Options: 'zerodha' / 'kite', 'yfinance' (default).
    """
    selected = (provider_name or settings.market_data_provider or "yfinance").lower()
    
    if selected in ("zerodha", "kite", "kiteconnect"):
        kite = ZerodhaKiteMarketProvider()
        if kite.is_configured():
            return kite
        logger.info("Zerodha Kite credentials not configured; routing to secondary provider (Yahoo Finance).")
        return YahooFinanceIndianProvider()
    
    return YahooFinanceIndianProvider()

__all__ = [
    "BaseMarketDataProvider",
    "YahooFinanceIndianProvider",
    "ZerodhaKiteMarketProvider",
    "get_market_provider"
]
