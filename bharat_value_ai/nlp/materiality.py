"""Financial Materiality Scoring Engine."""
from typing import Dict, Any

EVENT_MATERIALITY_WEIGHTS = {
    "FRAUD_ACCOUNTING": 0.98,
    "REGULATORY_ACTION": 0.92,
    "DEBT_RESTRUCTURING": 0.90,
    "EARNINGS_BEAT": 0.85,
    "EARNINGS_MISS": 0.85,
    "ORDER_WIN": 0.80,
    "CAPEX_EXPANSION": 0.78,
    "ACQUISITION_MERGER": 0.78,
    "PROMOTER_PLEDGE": 0.75,
    "MANAGEMENT_CHANGE": 0.70,
    "FUNDRAISING_DILUTION": 0.68,
    "PRODUCT_LAUNCH": 0.65,
    "DIVIDEND_BUYBACK": 0.60,
    "INDUSTRY_POLICY": 0.55,
    "LITIGATION_LEGAL": 0.72,
    "GENERAL_MARKET": 0.35
}

SOURCE_QUALITY_WEIGHTS = {
    "official_filing": 1.0,
    "financial_media": 0.85,
    "rss": 0.70
}

class MaterialityEngine:
    """Estimates financial materiality (0.0 to 1.0) and market-moving significance."""

    @staticmethod
    def calculate_materiality(
        event_category: str,
        source_category: str,
        has_monetary_value: bool,
        is_original_disclosure: bool
    ) -> float:
        base_event_weight = EVENT_MATERIALITY_WEIGHTS.get(event_category, 0.40)
        source_weight = SOURCE_QUALITY_WEIGHTS.get(source_category, 0.75)

        score = base_event_weight * 0.70 + source_weight * 0.20
        if has_monetary_value:
            score += 0.07
        if is_original_disclosure:
            score += 0.03

        return round(min(1.0, max(0.1, score)), 2)

materiality_engine = MaterialityEngine()
