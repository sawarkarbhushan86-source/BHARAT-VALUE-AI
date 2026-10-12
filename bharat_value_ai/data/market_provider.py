"""Indian Market Data Provider with NSE/BSE Trading Calendar and Live/Cached Abstraction."""
import datetime
import pytz
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from bharat_value_ai.data.normalization import (
    QuoteStatus, QuoteType, normalize_symbol, get_current_utc,
    get_current_ist, format_ist_timestamp
)
from bharat_value_ai.services.market_data_service import (
    market_data_service, check_indian_market_session, NSE_HOLIDAYS
)
from bharat_value_ai.data.providers.base import BaseMarketDataProvider

logger = logging.getLogger(__name__)
IST_TIMEZONE = pytz.timezone("Asia/Kolkata")

def is_indian_market_open() -> Dict[str, Any]:
    """Check if the National Stock Exchange (NSE) is currently open."""
    return check_indian_market_session()

class YahooFinanceIndianMarketProvider(BaseMarketDataProvider):
    """
    Bridge adapter routing to CentralMarketDataService while maintaining
    strict backwards compatibility with the existing test suite and endpoints.
    """

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance (NSE Delayed 15m)"

    def get_supported_symbols(self) -> List[str]:
        return market_data_service.provider.get_supported_symbols()

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch quote via centralized market data service."""
        return market_data_service.get_quote(symbol)

    def get_historical_ohlcv(self, symbol: str, period: str = "3mo", interval: str = "1d") -> List[Dict[str, Any]]:
        """Fetch real historical candles via centralized market data service."""
        return market_data_service.get_historical_ohlcv(symbol, period=period, interval=interval)

    def get_market_indices(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch Indian benchmark indices."""
        return market_data_service.get_market_indices(force_refresh=force_refresh)

    def get_provider_health(self) -> Dict[str, Any]:
        """Fetch provider operational status and connectivity."""
        return market_data_service.get_provider_health()

# Global default market provider instance
market_provider = YahooFinanceIndianMarketProvider()

