"""Market Data Quality Validation and Anomaly Detection."""
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from bharat_value_ai.data.normalization import get_current_utc, to_ist

class QualitySeverity:
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class MarketDataQualityReport(BaseModel):
    check_name: str
    symbol: str
    severity: str
    is_passed: bool
    details: str
    timestamp: datetime.datetime = Field(default_factory=get_current_utc)

class MarketDataQualityValidator:
    """Rigorous sanity checks for market quotes, candles, and corporate actions."""

    @staticmethod
    def validate_candle(
        symbol: str,
        open_p: float,
        high_p: float,
        low_p: float,
        close_p: float,
        volume: int,
        prev_close: Optional[float] = None
    ) -> List[MarketDataQualityReport]:
        """Verify geometric OHLC integrity, non-negativity, and extreme price spikes."""
        reports: List[MarketDataQualityReport] = []

        # 1. High must be >= Open, Low, Close
        if not (high_p >= open_p and high_p >= low_p and high_p >= close_p):
            reports.append(MarketDataQualityReport(
                check_name="OHLC_HIGH_VIOLATION",
                symbol=symbol,
                severity=QualitySeverity.CRITICAL,
                is_passed=False,
                details=f"High {high_p} is less than O={open_p}, L={low_p}, or C={close_p}"
            ))

        # 2. Low must be <= Open, High, Close
        if not (low_p <= open_p and low_p <= high_p and low_p <= close_p):
            reports.append(MarketDataQualityReport(
                check_name="OHLC_LOW_VIOLATION",
                symbol=symbol,
                severity=QualitySeverity.CRITICAL,
                is_passed=False,
                details=f"Low {low_p} is greater than O={open_p}, H={high_p}, or C={close_p}"
            ))

        # 3. Non-negative / Non-zero price
        if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0:
            reports.append(MarketDataQualityReport(
                check_name="ZERO_OR_NEGATIVE_PRICE",
                symbol=symbol,
                severity=QualitySeverity.CRITICAL,
                is_passed=False,
                details="Negative or zero price detected in candle data"
            ))

        # 4. Non-negative volume
        if volume < 0:
            reports.append(MarketDataQualityReport(
                check_name="NEGATIVE_VOLUME",
                symbol=symbol,
                severity=QualitySeverity.WARNING,
                is_passed=False,
                details=f"Negative volume observed: {volume}"
            ))

        # 5. Extreme single-day move (circuit filter / split anomaly check)
        if prev_close and prev_close > 0:
            pct_move = abs((close_p - prev_close) / prev_close) * 100
            if pct_move > 30.0:
                reports.append(MarketDataQualityReport(
                    check_name="UNUSUAL_PRICE_JUMP_CIRCUIT",
                    symbol=symbol,
                    severity=QualitySeverity.WARNING,
                    is_passed=False,
                    details=f"Price moved {pct_move:.1f}% from prev close ₹{prev_close}. Potential unadjusted stock split or bonus."
                ))

        return reports

    @staticmethod
    def validate_quote(quote: Dict[str, Any]) -> List[MarketDataQualityReport]:
        """Validate single quote snapshot."""
        reports: List[MarketDataQualityReport] = []
        sym = quote.get("symbol", "")
        price = quote.get("price", 0.0)

        if price <= 0:
            reports.append(MarketDataQualityReport(
                check_name="INVALID_QUOTE_PRICE",
                symbol=sym,
                severity=QualitySeverity.CRITICAL,
                is_passed=False,
                details=f"Invalid price ₹{price} for {sym}"
            ))

        # Check timestamp recency
        q_ts = quote.get("quote_timestamp")
        if q_ts:
            if isinstance(q_ts, str):
                try:
                    q_ts = datetime.datetime.fromisoformat(q_ts)
                except Exception:
                    q_ts = None
            if q_ts:
                now = get_current_utc()
                # If naive, assume UTC
                if q_ts.tzinfo is None:
                    q_ts = q_ts.replace(tzinfo=datetime.timezone.utc)
                age_hours = (now - q_ts).total_seconds() / 3600.0
                if age_hours > 72.0:
                    reports.append(MarketDataQualityReport(
                        check_name="STALE_QUOTE_OBSERVATION",
                        symbol=sym,
                        severity=QualitySeverity.INFO,
                        is_passed=True,
                        details=f"Quote observation is {age_hours:.1f} hours old (weekend or holiday observation)."
                    ))

        return reports

quality_validator = MarketDataQualityValidator()
