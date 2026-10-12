"""Unified Company Snapshot Service providing single-point-of-truth across all screens and exports."""
import datetime
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from bharat_value_ai.data.normalization import (
    QuoteStatus, normalize_symbol, get_current_utc, format_ist_timestamp
)
from bharat_value_ai.data.registry import company_registry
from bharat_value_ai.services.market_data_service import market_data_service
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.analysis.fair_value import fair_value_engine
from bharat_value_ai.analysis.quality_growth import quality_engine
from bharat_value_ai.analysis.risk_governance import risk_engine

class UnifiedCompanySnapshot(BaseModel):
    """Immutable single-point-of-truth snapshot consumed uniformly by UI, Agents, and Exports."""
    snapshot_id: str
    symbol: str
    canonical_id: str
    company_name: str
    sector: str
    industry: str
    is_financial: bool
    created_at_utc: datetime.datetime
    created_at_ist: str

    # Market Quote
    quote: Dict[str, Any]
    current_price: float
    price_status: str # "LIVE", "DELAYED", "LAST AVAILABLE", "DEMO", "UNAVAILABLE"
    price_timestamp_ist: str

    # Audited Financials
    fundamentals: Dict[str, Any]
    reporting_period: str
    filing_type: str

    # Valuation & Fair Value
    valuation: Dict[str, Any]
    fair_value: float
    margin_of_safety_pct: float
    valuation_status: str
    valuation_model_type: str

    # Business Quality & Risk
    quality_score: float
    compounding_tier: str
    active_risk_flags_count: int
    dupont_drivers: str


class SnapshotService:
    """Produces verified, single-point-of-truth company snapshots."""

    @staticmethod
    def get_snapshot(symbol: str) -> UnifiedCompanySnapshot:
        clean_sym = normalize_symbol(symbol)
        comp_meta = company_registry.get_company(clean_sym) or {}
        company_name = comp_meta.get("name", clean_sym)
        sector = comp_meta.get("sector", "Diversified")
        industry = comp_meta.get("industry", "Diversified")
        is_financial = bool(comp_meta.get("is_financial", False))

        now_utc = get_current_utc()
        now_ist_str = format_ist_timestamp(now_utc)
        snap_id = f"snap_{clean_sym}_{now_utc.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # 1. Fetch quote
        quote = market_data_service.get_quote(clean_sym)
        curr_price = quote.get("price", 0.0)
        p_status = quote.get("status", QuoteStatus.UNAVAILABLE.value)
        p_ts_ist = quote.get("retrieval_ist", now_ist_str)

        # 2. Fetch fundamentals & DuPont
        fund = fundamentals_engine.get_company_fundamentals(clean_sym)
        dupont = fundamentals_engine.compute_dupont_3_stage(fund)

        # 3. Evaluate valuation
        val = fair_value_engine.evaluate_valuation(clean_sym)

        # 4. Evaluate quality & risk
        qual = quality_engine.evaluate_company(clean_sym)
        risk_flags = risk_engine.evaluate_risks(clean_sym)

        return UnifiedCompanySnapshot(
            snapshot_id=snap_id,
            symbol=clean_sym,
            canonical_id=f"NSE:{clean_sym}",
            company_name=company_name,
            sector=sector,
            industry=industry,
            is_financial=is_financial,
            created_at_utc=now_utc,
            created_at_ist=now_ist_str,
            quote=quote,
            current_price=curr_price,
            price_status=p_status,
            price_timestamp_ist=p_ts_ist,
            fundamentals=fund,
            reporting_period=fund.get("reporting_period", "FY2023-24"),
            filing_type=fund.get("filing_type", "Consolidated Audited"),
            valuation=val.model_dump(),
            fair_value=val.composite_fair_value,
            margin_of_safety_pct=val.margin_of_safety_pct,
            valuation_status=val.valuation_status,
            valuation_model_type=val.model_type,
            quality_score=qual.composite_score,
            compounding_tier=qual.multibagger_potential_tier,
            active_risk_flags_count=len(risk_flags),
            dupont_drivers=dupont.get("interpretation", "")
        )

snapshot_service = SnapshotService()
