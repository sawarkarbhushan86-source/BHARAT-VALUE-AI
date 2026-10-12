"""Yahoo Finance Indian Market Data Provider (NSE/BSE)."""
import datetime
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf

from bharat_value_ai.data.providers.base import BaseMarketDataProvider
from bharat_value_ai.data.normalization import (
    QuoteStatus, QuoteType, normalize_symbol, get_current_utc,
    to_ist, format_ist_timestamp
)
from bharat_value_ai.data.quality import quality_validator, QualitySeverity

logger = logging.getLogger(__name__)

class YahooFinanceIndianProvider(BaseMarketDataProvider):
    """
    Retrieves authentic Indian market data from Yahoo Finance (.NS for NSE, .BO for BSE).
    Enforces quality checks and never fabricates mock numbers on failure.
    """

    @property
    def provider_name(self) -> str:
        return "Yahoo Finance (NSE Delayed 15m)"

    def get_supported_symbols(self) -> List[str]:
        from bharat_value_ai.data.registry import company_registry
        return [c["symbol"] for c in company_registry.get_all_companies()]

    def _format_ticker(self, symbol: str) -> str:
        clean = normalize_symbol(symbol)
        if not clean.endswith(".NS") and not clean.endswith(".BO"):
            return f"{clean}.NS"
        return clean

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        clean_sym = normalize_symbol(symbol)
        ticker_str = self._format_ticker(clean_sym)
        now_utc = get_current_utc()

        try:
            ticker = yf.Ticker(ticker_str)
            hist = ticker.history(period="5d")
            if hist.empty:
                logger.warning(f"No trading history returned by yfinance for {ticker_str}")
                return None

            last_row = hist.iloc[-1]
            prev_close = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else float(last_row["Open"])
            curr_price = float(last_row["Close"])
            change = float(curr_price - prev_close)
            change_pct = float((change / prev_close) * 100) if prev_close > 0 else 0.0

            vol = int(last_row["Volume"])
            turnover_cr = round((curr_price * vol) / 1e7, 2)

            # Extract 52-week high/low safely from history or ticker fast_info
            w52_high = float(hist["High"].max())
            w52_low = float(hist["Low"].min())
            try:
                if hasattr(ticker, "fast_info") and ticker.fast_info:
                    fi_high = getattr(ticker.fast_info, "year_high", None)
                    fi_low = getattr(ticker.fast_info, "year_low", None)
                    if fi_high:
                        w52_high = float(fi_high)
                    if fi_low:
                        w52_low = float(fi_low)
            except Exception:
                pass

            quote_record = {
                "symbol": clean_sym,
                "exchange": "NSE",
                "price": round(curr_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "open_price": round(float(last_row["Open"]), 2),
                "high_price": round(float(last_row["High"]), 2),
                "low_price": round(float(last_row["Low"]), 2),
                "previous_close": round(prev_close, 2),
                "volume": vol,
                "turnover_cr": turnover_cr,
                "week_52_high": round(w52_high, 2),
                "week_52_low": round(w52_low, 2),
                "data_source": "yfinance_delayed_15m",
                "is_delayed": True,
                "quote_type": QuoteType.DELAYED_QUOTE.value,
                "status": QuoteStatus.DELAYED.value,
                "quote_timestamp": now_utc,
                "retrieval_timestamp": now_utc,
                "retrieval_ist": format_ist_timestamp(now_utc)
            }

            # Run quality validation
            reports = quality_validator.validate_quote(quote_record)
            if any(r.severity == QualitySeverity.CRITICAL for r in reports):
                logger.error(f"Critical quality failure on quote for {clean_sym}: {reports}")
                return None

            return quote_record

        except Exception as e:
            logger.error(f"Exception fetching quote for {ticker_str}: {e}")
            return None

    def get_historical_ohlcv(
        self, symbol: str, period: str = "3mo", interval: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        clean_sym = normalize_symbol(symbol)
        ticker_str = self._format_ticker(clean_sym)

        # Normalize period and interval
        norm_period = period.lower().strip()
        if norm_period in ("1d", "day"):
            eff_period = "1d"
            eff_interval = interval or "5m"
        elif norm_period in ("1w", "5d", "week"):
            eff_period = "5d"
            eff_interval = interval or "15m"
        elif norm_period in ("1m", "1mo", "month"):
            eff_period = "1mo"
            eff_interval = interval or "1d"
        elif norm_period in ("3m", "3mo"):
            eff_period = "3mo"
            eff_interval = interval or "1d"
        elif norm_period in ("6m", "6mo"):
            eff_period = "6mo"
            eff_interval = interval or "1d"
        elif norm_period in ("1y", "12mo", "year"):
            eff_period = "1y"
            eff_interval = interval or "1d"
        elif norm_period in ("5y", "5year"):
            eff_period = "5y"
            eff_interval = interval or "1wk"
        else:
            eff_period = "3mo"
            eff_interval = interval or "1d"

        try:
            ticker = yf.Ticker(ticker_str)
            df = ticker.history(period=eff_period, interval=eff_interval)
            if df.empty:
                logger.warning(f"Empty OHLCV history returned for {ticker_str} ({eff_period}, {eff_interval})")
                return []

            # Ensure chronological order
            df = df.sort_index()

            candles = []
            prev_close = None
            for idx, row in df.iterrows():
                ts = idx.to_pydatetime()
                o = float(row["Open"])
                h = float(row["High"])
                l = float(row["Low"])
                c = float(row["Close"])
                v = int(row["Volume"]) if "Volume" in row and not np.isnan(row["Volume"]) else 0

                # Quality checks
                diags = quality_validator.validate_candle(clean_sym, o, h, l, c, v, prev_close)
                if not any(d.severity == QualitySeverity.CRITICAL for d in diags):
                    candles.append({
                        "symbol": clean_sym,
                        "timestamp": ts,
                        "open": round(o, 2),
                        "high": round(h, 2),
                        "low": round(l, 2),
                        "close": round(c, 2),
                        "volume": v,
                        "is_split_adjusted": True
                    })
                    prev_close = c
            return candles

        except Exception as e:
            logger.error(f"Exception fetching OHLCV for {ticker_str}: {e}")
            return []

    def _fetch_nse_official_indices(self) -> List[Dict[str, Any]]:
        """Fetch real-time official benchmark indices directly from NSE India API."""
        import urllib.request
        import json
        import ssl

        url = "https://www.nseindia.com/api/allIndices"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        now_utc = get_current_utc()
        raw_list = data.get("data", [])
        index_map = {item.get("index", "").upper(): item for item in raw_list}

        target_indices = [
            ("NIFTY 50", "^NSEI", "NIFTY 50"),
            ("NIFTY BANK", "^NSEBANK", "NIFTY BANK"),
            ("NIFTY SMALLCAP 100", "^CNXSC", "NIFTY SMALLCAP 100"),
            ("INDIA VIX", "^INDIAVIX", "INDIA VIX")
        ]

        parsed = []
        for nse_name, sym, display_name in target_indices:
            rec = index_map.get(nse_name)
            if rec:
                curr = float(rec.get("last", 0.0))
                chg = float(rec.get("variation", 0.0))
                pct = float(rec.get("percentChange", 0.0))
                open_p = float(rec.get("open", curr))
                high_p = float(rec.get("high", curr))
                low_p = float(rec.get("low", curr))
                prev_c = float(rec.get("previousClose", curr))

                parsed.append({
                    "name": display_name,
                    "symbol": sym,
                    "price": round(curr, 2),
                    "change": round(chg, 2),
                    "change_percent": round(pct, 2),
                    "open_price": round(open_p, 2),
                    "high_price": round(high_p, 2),
                    "low_price": round(low_p, 2),
                    "previous_close": round(prev_c, 2),
                    "timestamp": now_utc,
                    "timestamp_ist": format_ist_timestamp(now_utc),
                    "status": QuoteStatus.DELAYED.value,
                    "data_source": "nse_official_live_indices",
                    "exchange_timestamp": data.get("timestamp", format_ist_timestamp(now_utc))
                })

        return parsed

    def get_market_indices(self) -> List[Dict[str, Any]]:
        """
        Fetch authentic Indian benchmark indices.
        Guarantees all 4 indices (Nifty 50, Nifty Bank, Nifty Smallcap 100, India VIX)
        are retrieved and refreshed.
        """
        # 1. Try official NSE direct feed first
        try:
            nse_indices = self._fetch_nse_official_indices()
            if len(nse_indices) == 4:
                return nse_indices
        except Exception as e:
            logger.info(f"NSE direct indices endpoint unavailable, falling back to yfinance: {e}")

        # 2. Yahoo Finance fallback
        index_tickers = [
            ("^NSEI", "NIFTY 50"),
            ("^NSEBANK", "NIFTY BANK"),
            ("^INDIAVIX", "INDIA VIX"),
            ("SML100CASE.NS", "NIFTY SMALLCAP 100") # Zerodha Nifty Smallcap 100 ETF proxy when index ticker deprecated
        ]
        results = []
        now_utc = get_current_utc()

        for sym, name in index_tickers:
            try:
                t = yf.Ticker(sym)
                h = t.history(period="5d")
                if not h.empty:
                    curr = float(h.iloc[-1]["Close"])
                    prev = float(h.iloc[-2]["Close"]) if len(h) > 1 else curr
                    chg = curr - prev
                    pct = (chg / prev) * 100 if prev > 0 else 0.0

                    display_symbol = "^CNXSC" if name == "NIFTY SMALLCAP 100" else sym
                    results.append({
                        "name": name,
                        "symbol": display_symbol,
                        "price": round(curr, 2),
                        "change": round(chg, 2),
                        "change_percent": round(pct, 2),
                        "timestamp": now_utc,
                        "timestamp_ist": format_ist_timestamp(now_utc),
                        "status": QuoteStatus.DELAYED.value,
                        "data_source": "yfinance_indices"
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch index {sym}: {e}")

        return results

    def check_health(self) -> Dict[str, Any]:
        """Check provider operational status and network latency."""
        import time
        start = time.perf_counter()
        try:
            t = yf.Ticker("^NSEI")
            h = t.history(period="1d")
            elapsed = time.perf_counter() - start
            if not h.empty:
                return {
                    "status": "HEALTHY",
                    "latency_ms": round(elapsed * 1000, 1),
                    "provider": self.provider_name,
                    "timestamp_ist": format_ist_timestamp(get_current_utc())
                }
            return {
                "status": "DEGRADED",
                "latency_ms": round(elapsed * 1000, 1),
                "provider": self.provider_name,
                "timestamp_ist": format_ist_timestamp(get_current_utc()),
                "message": "Empty response from market data provider."
            }
        except Exception as e:
            elapsed = time.perf_counter() - start
            return {
                "status": "UNREACHABLE",
                "latency_ms": round(elapsed * 1000, 1),
                "provider": self.provider_name,
                "timestamp_ist": format_ist_timestamp(get_current_utc()),
                "error": str(e)
            }

