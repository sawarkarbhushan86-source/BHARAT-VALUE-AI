"""Market Data Provider Abstraction Layer."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseMarketDataProvider(ABC):
    """Abstract interface for external Indian market data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the data provider (e.g. 'yfinance', 'nse_bhavcopy', 'alpha_vantage')."""
        pass

    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """List of supported canonical or exchange ticker symbols."""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current market quote for a symbol.
        Returns None or raises an exception if the provider cannot retrieve the quote.
        MUST NOT fabricate synthetic data.
        """
        pass

    @abstractmethod
    def get_historical_ohlcv(
        self, symbol: str, period: str = "3mo", interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLCV candles.
        Returns list of candle dicts or empty list if unavailable.
        MUST NOT fabricate synthetic candles.
        """
        pass

    @abstractmethod
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Fetch Indian benchmark indices (Nifty 50, Nifty Smallcap 100, Nifty Bank, India VIX)."""
        pass
