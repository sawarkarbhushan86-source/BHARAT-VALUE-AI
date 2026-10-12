"""Tests for Canonical Symbol Resolution, Security Master, and Universe Coverage."""
import pytest
from bharat_value_ai.data.canonical_resolver import resolve_canonical_symbol
from bharat_value_ai.data.security_master import security_master
from bharat_value_ai.data.normalization import normalize_symbol
from bharat_value_ai.services.market_data_service import market_data_service


def test_resolve_canonical_symbol_aliases():
    """Verify company names, colloquials, and tickers resolve to canonical symbols."""
    cases = [
        ("Reliance Industries", "RELIANCE"),
        ("Reliance Industries Ltd", "RELIANCE"),
        ("RELIANCE INDUSTRIES", "RELIANCE"),
        ("TCS", "TCS"),
        ("Tata Consultancy Services", "TCS"),
        ("HDFC Bank", "HDFCBANK"),
        ("HDFC Bank Limited", "HDFCBANK"),
        ("SBI", "SBIN"),
        ("State Bank of India", "SBIN"),
        ("State Bank", "SBIN"),
        ("L&T", "LT"),
        ("Larsen & Toubro", "LT"),
        ("Bharti Airtel", "BHARTIARTL"),
        ("Tata Motors", "TATAMOTORS"),
        ("ITC", "ITC"),
        ("Infosys", "INFY"),
        ("Asian Paints", "ASIANPAINT"),
        ("Kotak Bank", "KOTAKBANK"),
        ("Axis Bank", "AXISBANK"),
        ("Maruti Suzuki", "MARUTI"),
        ("Sun Pharma", "SUNPHARMA"),
        ("Titan Company", "TITAN"),
        ("Nifty BeES", "NIFTYBEES"),
        ("Bank BeES", "BANKBEES"),
    ]
    for raw_input, expected in cases:
        resolved = resolve_canonical_symbol(raw_input)
        assert resolved == expected, f"Failed for {raw_input}: got {resolved}, expected {expected}"


def test_resolve_canonical_symbol_isin_and_bse():
    """Verify ISIN codes and BSE security codes resolve to NSE tradingsymbol."""
    assert resolve_canonical_symbol("INE002A01018") == "RELIANCE"
    assert resolve_canonical_symbol("500325") == "RELIANCE"
    assert resolve_canonical_symbol("INE467B01029") == "TCS"
    assert resolve_canonical_symbol("532540") == "TCS"
    assert resolve_canonical_symbol("INE040A01034") == "HDFCBANK"
    assert resolve_canonical_symbol("INE062A01020") == "SBIN"


def test_security_master_canonical_schema():
    """Verify SecurityMaster contains institutional normalized schema and metadata."""
    entries = security_master.list_entries()
    assert len(entries) >= 50, f"Expected >= 50 securities, found {len(entries)}"

    reliance = security_master.get_entry("RELIANCE")
    assert reliance is not None
    assert reliance.tradingsymbol == "RELIANCE"
    assert reliance.company_name == "Reliance Industries Limited"
    assert reliance.exchange == "NSE"
    assert reliance.instrument_token == 738561
    assert reliance.isin == "INE002A01018"
    assert reliance.series == "EQ"
    assert reliance.instrument_type in ["EQ", "EQUITY"]
    assert reliance.listing_status == "ACTIVE"
    assert reliance.last_synced_at is not None

    stats = security_master.get_universe_stats()
    assert stats["total_instruments"] >= 50
    assert stats["active_instruments"] >= 50
    assert "last_synced_at" in stats


def test_normalize_symbol_with_exchange_prefixes():
    """Verify symbol normalizer strips prefixes while resolving company names."""
    assert normalize_symbol("NSE:RELIANCE") == "RELIANCE"
    assert normalize_symbol("BSE:TCS") == "TCS"
    assert normalize_symbol("RELIANCE.NS") == "RELIANCE"
    assert normalize_symbol("TCS.BO") == "TCS"
    assert normalize_symbol("Reliance Industries") == "RELIANCE"


def test_market_data_service_resolves_reliance_industries():
    """Verify market_data_service.get_quote('Reliance Industries') resolves to RELIANCE and returns quote."""
    quote = market_data_service.get_quote("Reliance Industries")
    assert quote["symbol"] == "RELIANCE"
    assert quote["price"] > 0
    assert quote["status"] in ["LIVE", "DELAYED", "LAST AVAILABLE"]
    assert quote["exchange"] in ["NSE", "BSE"]
