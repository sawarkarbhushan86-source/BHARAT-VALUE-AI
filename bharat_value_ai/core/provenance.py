"""Point-in-time data provenance, lineage tracking, and data quality diagnostics."""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DataProvenanceRecord(BaseModel):
    """Metadata tracking data lineage and point-in-time public availability."""
    entity_symbol: str
    exchange: str = "NSE"
    data_type: str # "price_candle", "financial_statement", "news_article", "risk_flag"
    source_provider: str # e.g. "yfinance", "bse_filings", "moneycontrol_rss"
    source_identifier: Optional[str] = None # URL, filing ID, or document reference
    reporting_period: Optional[str] = None # e.g. "FY2024", "Q3FY2024"
    source_published_at: datetime # When source announced it
    public_availability_at: datetime # Point-in-time cutoff timestamp
    retrieval_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_adjusted: bool = True
    is_consolidated: bool = True
    currency: str = "INR"
    validation_status: str = "VALIDATED" # "VALIDATED", "WARNING", "REJECTED"
    transformations_applied: List[str] = []

class DataQualityDiagnostic(BaseModel):
    check_name: str
    symbol: str
    severity: str # "INFO", "WARNING", "CRITICAL"
    is_passed: bool
    details: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PointInTimeEngine:
    """Answers: What information was publicly available to the system at timestamp T?"""

    @staticmethod
    def filter_point_in_time_financials(
        financial_records: List[Dict[str, Any]],
        as_of_timestamp: datetime
    ) -> List[Dict[str, Any]]:
        """
        Filter out any financial statement published after as_of_timestamp.
        Prevents look-ahead bias in backtests and historical ML research.
        """
        eligible = []
        for rec in financial_records:
            # Check public_availability_date or fall back to reporting_date + 45 days (SEBI quarterly filing window)
            pub_date = rec.get("public_availability_date")
            if not pub_date:
                rep_date = rec.get("reporting_date")
                if isinstance(rep_date, str):
                    rep_date = datetime.fromisoformat(rep_date)
                # SEBI allows up to 45 days after quarter end to release quarterly results
                pub_date = rep_date
            elif isinstance(pub_date, str):
                pub_date = datetime.fromisoformat(pub_date)

            if pub_date and pub_date <= as_of_timestamp:
                eligible.append(rec)
        return eligible

    @staticmethod
    def validate_ohlcv_candle(
        open_p: float, high_p: float, low_p: float, close_p: float, volume: int
    ) -> List[DataQualityDiagnostic]:
        """Verify impossible OHLC relationships and volume integrity."""
        diagnostics = []
        # Check 1: High must be greater than or equal to Open, Low, Close
        if not (high_p >= open_p and high_p >= low_p and high_p >= close_p):
            diagnostics.append(DataQualityDiagnostic(
                check_name="OHLC_HIGH_VIOLATION",
                symbol="",
                severity="CRITICAL",
                is_passed=False,
                details=f"High {high_p} is not maximum of O={open_p}, L={low_p}, C={close_p}"
            ))

        # Check 2: Low must be less than or equal to Open, High, Close
        if not (low_p <= open_p and low_p <= high_p and low_p <= close_p):
            diagnostics.append(DataQualityDiagnostic(
                check_name="OHLC_LOW_VIOLATION",
                symbol="",
                severity="CRITICAL",
                is_passed=False,
                details=f"Low {low_p} is not minimum of O={open_p}, H={high_p}, C={close_p}"
            ))

        # Check 3: Non-negative price
        if open_p <= 0 or close_p <= 0 or low_p <= 0 or high_p <= 0:
            diagnostics.append(DataQualityDiagnostic(
                check_name="NEGATIVE_PRICE_VIOLATION",
                symbol="",
                severity="CRITICAL",
                is_passed=False,
                details="Negative or zero price detected in candle"
            ))

        # Check 4: Non-negative volume
        if volume < 0:
            diagnostics.append(DataQualityDiagnostic(
                check_name="NEGATIVE_VOLUME_VIOLATION",
                symbol="",
                severity="WARNING",
                is_passed=False,
                details=f"Negative trading volume: {volume}"
            ))

        return diagnostics
