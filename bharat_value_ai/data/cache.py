"""Market Data Cache and Last-Verified-Observation Store."""
import datetime
from typing import Dict, Any, Optional, List
import copy

from bharat_value_ai.data.normalization import (
    QuoteStatus, QuoteType, get_current_utc, to_ist, format_ist_timestamp
)

class MarketDataCacheManager:
    """
    Manages in-memory TTL caching and preserves genuine verified historical observations.
    Never fabricates synthetic data upon cache misses or network failures.
    """

    def __init__(self, default_ttl_seconds: int = 300):
        self.default_ttl = default_ttl_seconds
        self._quote_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime.datetime] = {}
        self._last_verified_observations: Dict[str, Dict[str, Any]] = {}
        self._index_cache: List[Dict[str, Any]] = []
        self._index_cache_timestamp: Optional[datetime.datetime] = None
        self._index_ttl_seconds = 60
        self._hits = 0
        self._misses = 0

    def get_cached_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Return cached quote if still within TTL."""
        sym = symbol.upper()
        if sym in self._quote_cache:
            ts = self._cache_timestamps.get(sym)
            if ts:
                now = get_current_utc()
                age = (now - ts).total_seconds()
                if age <= self.default_ttl:
                    self._hits += 1
                    cached = copy.deepcopy(self._quote_cache[sym])
                    cached["quote_type"] = QuoteType.CACHED_QUOTE.value
                    cached["cache_age_seconds"] = round(age, 1)
                    return cached
        self._misses += 1
        return None

    def store_baseline_observation(self, symbol: str, quote: Dict[str, Any]):
        """
        Store audited baseline closing observation strictly as fallback when upstream is offline.
        Does NOT populate the active live quote cache.
        """
        sym = symbol.upper()
        verified_rec = copy.deepcopy(quote)
        verified_rec["is_baseline_fallback"] = True
        self._last_verified_observations[sym] = verified_rec

    def store_verified_quote(self, symbol: str, quote: Dict[str, Any]):
        """Store successfully fetched verified quote into live TTL cache and observation history."""
        sym = symbol.upper()
        now = get_current_utc()

        quote_copy = copy.deepcopy(quote)
        self._quote_cache[sym] = quote_copy
        self._cache_timestamps[sym] = now

        # Update last verified observation
        verified_rec = copy.deepcopy(quote)
        verified_rec["last_verified_at"] = now
        verified_rec["last_verified_ist"] = format_ist_timestamp(now)
        self._last_verified_observations[sym] = verified_rec

    def get_last_verified_observation(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Return the last genuinely verified observation when provider is unreachable.
        Explicitly labeled with QuoteStatus.LAST_AVAILABLE / STALE.
        """
        sym = symbol.upper()
        if sym in self._last_verified_observations:
            obs = copy.deepcopy(self._last_verified_observations[sym])
            obs["status"] = QuoteStatus.LAST_AVAILABLE.value
            obs["quote_type"] = QuoteType.ADJUSTED_HISTORICAL_CLOSE.value
            obs["is_delayed"] = True
            obs["is_stale"] = True
            obs["note"] = "Provider offline or market closed; displaying last verified historical observation."
            return obs
        return None

    def store_index_cache(self, indices: List[Dict[str, Any]]):
        """Cache verified index quotes."""
        self._index_cache = copy.deepcopy(indices)
        self._index_cache_timestamp = get_current_utc()

    def get_cached_indices(self, max_age_seconds: int = 60) -> Optional[List[Dict[str, Any]]]:
        """Return cached benchmark indices if within TTL."""
        if self._index_cache and self._index_cache_timestamp:
            age = (get_current_utc() - self._index_cache_timestamp).total_seconds()
            if age <= max_age_seconds:
                return copy.deepcopy(self._index_cache)
        return None

    def invalidate(self, symbol: Optional[str] = None):
        """Invalidate cache for specific symbol or all symbols."""
        if symbol:
            sym = symbol.upper()
            self._quote_cache.pop(sym, None)
            self._cache_timestamps.pop(sym, None)
        else:
            self._quote_cache.clear()
            self._cache_timestamps.clear()
            self._index_cache.clear()
            self._index_cache_timestamp = None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "cached_symbols_count": len(self._quote_cache),
            "last_verified_count": len(self._last_verified_observations),
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio_pct": round((self._hits / (self._hits + self._misses) * 100), 2) if (self._hits + self._misses) > 0 else 0.0
        }


market_cache = MarketDataCacheManager()

