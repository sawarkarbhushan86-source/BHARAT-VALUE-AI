"""Data Normalization, Canonical Identifiers, and India Standard Time (IST) Handlers."""
import datetime
from enum import Enum
from typing import Dict, Any, Optional, Tuple
import pytz

IST_TIMEZONE = pytz.timezone("Asia/Kolkata")
UTC_TIMEZONE = datetime.timezone.utc

class QuoteStatus(str, Enum):
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    LAST_AVAILABLE = "LAST AVAILABLE"
    STALE = "STALE"
    DEMO = "DEMO"
    UNAVAILABLE = "UNAVAILABLE"


class QuoteType(str, Enum):
    LAST_TRADED_PRICE = "last_traded_price"
    PREVIOUS_CLOSE = "previous_close"
    ADJUSTED_HISTORICAL_CLOSE = "adjusted_historical_close"
    INTRADAY_QUOTE = "intraday_quote"
    DELAYED_QUOTE = "delayed_quote"
    CACHED_QUOTE = "cached_quote"

class CurrencyUnit(str, Enum):
    INR = "INR"

def get_current_utc() -> datetime.datetime:
    """Returns current datetime with UTC timezone."""
    return datetime.datetime.now(UTC_TIMEZONE)

def get_current_ist() -> datetime.datetime:
    """Returns current datetime in Asia/Kolkata timezone."""
    return datetime.datetime.now(IST_TIMEZONE)

def to_ist(dt: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    """Convert any datetime to Asia/Kolkata timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC if naive
        dt = dt.replace(tzinfo=UTC_TIMEZONE)
    return dt.astimezone(IST_TIMEZONE)

def format_ist_timestamp(dt: Optional[datetime.datetime]) -> str:
    """Format datetime as a clear IST string."""
    if dt is None:
        return "N/A"
    ist_dt = to_ist(dt)
    return ist_dt.strftime("%Y-%m-%d %H:%M:%S IST")

def normalize_symbol(raw_symbol: str) -> str:
    """
    Normalizes any exchange ticker symbol, company name, ISIN, or alias into standard canonical symbol.
    Strips '.NS', '.BO', exchange prefixes, whitespace, and resolves company names.
    """
    if not raw_symbol:
        return ""
    from bharat_value_ai.data.canonical_resolver import resolve_canonical_symbol
    return resolve_canonical_symbol(raw_symbol)

def format_inr_crores(value: Optional[float], decimals: int = 2) -> str:
    """Format numeric value in INR Crores (₹X.XX Cr)."""
    if value is None:
        return "N/A"
    return f"₹{value:,.{decimals}f} Cr"

def format_inr_price(value: Optional[float], decimals: int = 2) -> str:
    """Format share price in INR (₹X.XX)."""
    if value is None:
        return "N/A"
    return f"₹{value:,.{decimals}f}"

def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """Format percentage value (+X.XX% / -X.XX%)."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"
