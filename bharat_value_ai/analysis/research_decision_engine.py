"""Beginner-Friendly Investment Research Decision Engine."""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel

from bharat_value_ai.services.snapshot_service import snapshot_service, UnifiedCompanySnapshot
from bharat_value_ai.data.normalization import normalize_symbol

class ResearchAssessment(str, Enum):
    WORTH_INVESTIGATING = "Worth investigating"
    POTENTIALLY_ATTRACTIVE = "Potentially attractive at the modeled valuation"
    FAIRLY_VALUED = "Fairly valued"
    EXPENSIVE = "Expensive relative to modeled fundamentals"
    ELEVATED_RISK = "Elevated business or financial risk"
    INSUFFICIENT_DATA = "Insufficient verified data"

class InvestmentHorizon(str, Enum):
    SHORT_TERM = "short_term" # 1-3 months (sentiment, valuation multiples, liquidity)
    MEDIUM_TERM = "medium_term" # 1-3 years (earnings trajectory, capex gestation, cyclical recovery)
    LONG_TERM = "long_term" # 3-5 years (capital allocation, ROE/ROCE compounding, competitive moat)

class MetricExplanation(BaseModel):
    metric_name: str
    display_value: str
    meaning: str
    why_it_matters: str
    sector_context: str
    limitations: str

class BeginnerResearchSummary(BaseModel):
    symbol: str
    company_name: str
    horizon: str
    assessment: str
    plain_english_summary: str
    strongest_supporting_evidence: str
    strongest_counterargument: str
    current_valuation_vs_range: str
    business_quality_and_health: str
    growth_drivers_and_assumptions: str
    material_risks_and_downside: str
    data_freshness_and_completeness: str
    confidence_limitations: str
    conditions_to_change_assessment: str
    metric_educational_drawers: List[MetricExplanation]

    # UI Convenience / Compatibility Fields
    assessment_label: Optional[str] = None
    headline: Optional[str] = None
    valuation_assessment: Optional[Dict[str, Any]] = None
    business_quality: Optional[Dict[str, Any]] = None
    evidence_points: Optional[List[str]] = None
    counterarguments: Optional[List[str]] = None
    growth_drivers: Optional[List[str]] = None
    material_risks: Optional[List[str]] = None
    data_freshness_statement: Optional[str] = None
    thesis_breakers: Optional[List[str]] = None
    educational_drawers: Optional[List[Dict[str, Any]]] = None


class ResearchDecisionEngine:
    """
    Translates complex quantitative fundamentals into objective,
    evidence-grounded, beginner-friendly research conclusions.
    Explicitly refuses to give unconditional 'Buy/Sell' recommendations.
    """

    @staticmethod
    def generate_summary(
        symbol: str, horizon: Any = InvestmentHorizon.MEDIUM_TERM
    ) -> BeginnerResearchSummary:
        if isinstance(horizon, str):
            try:
                horizon = InvestmentHorizon(horizon)
            except ValueError:
                horizon = InvestmentHorizon.MEDIUM_TERM
        clean_sym = normalize_symbol(symbol)
        snapshot: UnifiedCompanySnapshot = snapshot_service.get_snapshot(clean_sym)

        fund = snapshot.fundamentals
        val = snapshot.valuation
        curr_price = snapshot.current_price
        fair_val = snapshot.fair_value
        mos = snapshot.margin_of_safety_pct
        qual_score = snapshot.quality_score
        is_fin = snapshot.is_financial

        # 1. Check for insufficient data
        if not fund.get("is_catalogued", True) or snapshot.price_status == "UNAVAILABLE":
            drawers_inst = ResearchDecisionEngine._build_educational_drawers(snapshot)
            edu_ui = [
                {
                    "metric": d.metric_name,
                    "company_specific_value": d.display_value,
                    "definition": d.meaning,
                    "why_it_matters": d.why_it_matters,
                    "sector_context": d.sector_context,
                    "limitations": d.limitations
                }
                for d in drawers_inst
            ]
            insufficient_msg = (
                f"There is currently insufficient verified financial reporting data for {clean_sym} to form "
                "a defensible research view. The platform refuses to formulate unverified conjectures."
            )
            return BeginnerResearchSummary(
                symbol=clean_sym,
                company_name=snapshot.company_name,
                horizon=horizon.value,
                assessment=ResearchAssessment.INSUFFICIENT_DATA.value,
                plain_english_summary=insufficient_msg,
                strongest_supporting_evidence="Company is publicly listed on the exchange.",
                strongest_counterargument="Audited historical financial statements and segment disclosures have not yet been fully indexed.",
                current_valuation_vs_range="Valuation models cannot be reliably computed without audited financial baseline.",
                business_quality_and_health="Financial metrics are awaiting statutory ingestion.",
                growth_drivers_and_assumptions="Growth runway cannot be verified without primary annual report filings.",
                material_risks_and_downside="Incomplete surveillance coverage poses information asymmetry risk.",
                data_freshness_and_completeness="Data is incomplete; awaiting corporate filing ingestion.",
                confidence_limitations="High uncertainty due to lack of verifiable financial disclosures.",
                conditions_to_change_assessment="Upload or ingestion of official audited Annual Report accounts.",
                metric_educational_drawers=drawers_inst,
                # UI Convenience / Compatibility Fields
                assessment_label=ResearchAssessment.INSUFFICIENT_DATA.value,
                headline=insufficient_msg,
                valuation_assessment={
                    "current_price": curr_price,
                    "fair_value": fair_val,
                    "margin_of_safety_pct": mos,
                    "valuation_status": snapshot.valuation_status,
                    "model_type": snapshot.valuation_model_type
                },
                business_quality={
                    "quality_score": qual_score,
                    "compounding_tier": snapshot.compounding_tier,
                    "solvency_status": "Awaiting Data"
                },
                evidence_points=["Company is publicly listed on the exchange."],
                counterarguments=["Audited historical financial statements and segment disclosures have not yet been fully indexed."],
                growth_drivers=["Growth runway cannot be verified without primary annual report filings."],
                material_risks=["Incomplete surveillance coverage poses information asymmetry risk."],
                data_freshness_statement="Data is incomplete; awaiting corporate filing ingestion.",
                thesis_breakers=["Upload or ingestion of official audited Annual Report accounts."],
                educational_drawers=edu_ui
            )

        # 2. Formulate Evidence-Based Assessment
        roe = fund.get("roe_pct") or 0.0
        roce = fund.get("roce_pct") or 0.0
        dte = fund.get("debt_to_equity")
        ic = fund.get("interest_coverage")
        z_score = fund.get("altman_z_score")
        active_risks = snapshot.active_risk_flags_count

        # Determine Primary Assessment Category
        if active_risks >= 3 or (z_score and z_score < 1.81) or (dte and dte > 2.5):
            assessment = ResearchAssessment.ELEVATED_RISK
        elif mos > 15.0 and qual_score >= 65.0:
            assessment = ResearchAssessment.POTENTIALLY_ATTRACTIVE
        elif mos > 5.0 and qual_score >= 60.0:
            assessment = ResearchAssessment.WORTH_INVESTIGATING
        elif -15.0 <= mos <= 15.0:
            assessment = ResearchAssessment.FAIRLY_VALUED
        else:
            assessment = ResearchAssessment.EXPENSIVE

        # Formulate Horizon-Specific Plain English Summary
        if horizon == InvestmentHorizon.SHORT_TERM:
            summary = (
                f"Over a short-term horizon (1–3 months), {snapshot.company_name} is currently classified as '{assessment.value}'. "
                f"The verified price is ₹{curr_price:,.2f} with market quote status '{snapshot.price_status}'. "
                f"Short-term research focuses on recent quarterly momentum, media sentiment, and valuation stretch relative to immediate peers."
            )
        elif horizon == InvestmentHorizon.MEDIUM_TERM:
            summary = (
                f"Over a 1–3 year horizon, {snapshot.company_name} is evaluated as '{assessment.value}'. "
                f"Estimated composite fair value is ₹{fair_val:,.2f} versus the verified price of ₹{curr_price:,.2f} "
                f"(modeled margin of safety: {mos:+.1f}%). "
                f"Medium-term thesis depends on earnings trajectory, capacity utilization, and sector demand trends."
            )
        else: # LONG_TERM
            summary = (
                f"Over a 3–5 year compounding horizon, {snapshot.company_name} is assessed as '{assessment.value}'. "
                f"Business quality score is {qual_score:.1f}/100 ('{snapshot.compounding_tier}'). "
                f"Long-term outcomes will be dictated primarily by Return on Capital efficiency ({roce:.1f}% ROCE) "
                f"and reinvestment discipline rather than short-term price swings."
            )

        # Supporting Evidence & Counterarguments
        if is_fin:
            supporting_evidence = (
                f"Strong franchise fundamentals: Reported Return on Equity (ROE) of {roe:.1f}% and healthy capital position. "
                f"Valuation model applies sector-appropriate Justified P/B and Residual Income rather than industrial net debt."
            )
            counterargument = (
                "Vulnerable to potential asset-quality slippages, systemic interest rate cycles, and regulatory compliance shifts by the RBI."
            )
        else:
            supporting_evidence = (
                f"Consistent capital return profile: ROE of {roe:.1f}%, ROCE of {roce:.1f}%, and operating cash generation. "
                f"DuPont breakdown confirms: {snapshot.dupont_drivers}."
            )
            counterargument = (
                f"Smallcap cyclicality and raw material exposure. Modeled margin of safety is {mos:+.1f}%, "
                f"with bear case estimate standing at ₹{val.get('bear_case_value', 0):,.2f}."
            )

        # Range Breakdown
        bear_case = val.get("bear_case_value", 0.0)
        bull_case = val.get("bull_case_value", 0.0)
        val_range_str = (
            f"Verified Price: ₹{curr_price:,.2f} | Modeled Fair Value: ₹{fair_val:,.2f} "
            f"(Bear Scenario: ₹{bear_case:,.2f} ← Base: ₹{fair_val:,.2f} → Bull Scenario: ₹{bull_case:,.2f}). "
            f"Margin of Safety: {mos:+.1f}% ({val.get('valuation_status', 'N/A')})."
        )

        health_str = (
            f"Quality Score: {qual_score:.1f}/100. " +
            ("Financial Institution (Banking/NBFC) balance sheet." if is_fin else f"Debt-to-Equity: {dte or 0.0}x | Altman Z-Score: {z_score or 'N/A'}.")
        )

        growth_str = (
            f"Historical 3-Year Sales CAGR: {fund.get('revenue_growth_3y_cagr', 'N/A')}% | Profit CAGR: {fund.get('profit_growth_3y_cagr', 'N/A')}%. "
            f"Model assumes terminal growth anchor of {val.get('assumptions', {}).get('terminal_growth_rate', 0.05)*100:.1f}%."
        )

        risk_str = (
            f"Surveillance detected {active_risks} active forensic/governance risk indicators. "
            "Downside triggers include macro deceleration, raw material inflation, or valuation de-rating."
        )

        freshness_str = (
            f"Market quote retrieved at {snapshot.price_timestamp_ist} (Status: {snapshot.price_status}). "
            f"Financial statement period: {snapshot.reporting_period} ({snapshot.filing_type})."
        )

        conf_str = (
            "Confidence is bounded by reliance on reported statutory figures and macroeconomic assumptions (WACC and Cost of Equity). "
            "Projections are quantitative model estimates, NOT guaranteed outcomes."
        )

        cond_str = (
            "Assessment would become more favorable if market price drops below modeled bear case or earnings growth accelerates. "
            "Assessment would downgrade if Return on Equity declines or unexpected governance red flags emerge."
        )

        val_assessment = {
            "current_price": curr_price,
            "fair_value": fair_val,
            "margin_of_safety_pct": mos,
            "valuation_status": snapshot.valuation_status,
            "model_type": snapshot.valuation_model_type,
            "conservative_bound": val.get("bear_case_value", fair_val * 0.8),
            "aggressive_bound": val.get("bull_case_value", fair_val * 1.2)
        }

        biz_quality = {
            "quality_score": qual_score,
            "compounding_tier": snapshot.compounding_tier,
            "solvency_status": "Adequate" if (fund.get("debt_to_equity") is None or fund.get("debt_to_equity") <= 1.0) else "Leveraged"
        }

        drawers = ResearchDecisionEngine._build_educational_drawers(snapshot)
        edu_drawers_ui = [
            {
                "metric": d.metric_name,
                "company_specific_value": d.display_value,
                "definition": d.meaning,
                "why_it_matters": d.why_it_matters,
                "sector_context": d.sector_context,
                "limitations": d.limitations
            }
            for d in drawers
        ]

        return BeginnerResearchSummary(
            symbol=clean_sym,
            company_name=snapshot.company_name,
            horizon=horizon.value,
            assessment=assessment.value,
            plain_english_summary=summary,
            strongest_supporting_evidence=supporting_evidence,
            strongest_counterargument=counterargument,
            current_valuation_vs_range=val_range_str,
            business_quality_and_health=health_str,
            growth_drivers_and_assumptions=growth_str,
            material_risks_and_downside=risk_str,
            data_freshness_and_completeness=freshness_str,
            confidence_limitations=conf_str,
            conditions_to_change_assessment=cond_str,
            metric_educational_drawers=drawers,
            # UI Convenience / Compatibility Fields
            assessment_label=assessment.value,
            headline=summary,
            valuation_assessment=val_assessment,
            business_quality=biz_quality,
            evidence_points=[supporting_evidence],
            counterarguments=[counterargument],
            growth_drivers=[growth_str],
            material_risks=[risk_str],
            data_freshness_statement=freshness_str,
            thesis_breakers=[cond_str],
            educational_drawers=edu_drawers_ui
        )

    @staticmethod
    def _build_educational_drawers(snapshot: UnifiedCompanySnapshot) -> List[MetricExplanation]:
        fund = snapshot.fundamentals
        val = snapshot.valuation

        roce_val = f"{fund.get('roce_pct', 'N/A')}%"
        dte_val = f"{fund.get('debt_to_equity', 'N/A')}x" if not snapshot.is_financial else "N/A (Bank/NBFC)"
        mos_val = f"{snapshot.margin_of_safety_pct:+.1f}%"
        fcf_val = f"₹{fund.get('free_cash_flow', 'N/A')} Cr"

        return [
            MetricExplanation(
                metric_name="ROCE (Return on Capital Employed)",
                display_value=roce_val,
                meaning="How efficiently the business generates operating profit from all capital invested (debt + equity).",
                why_it_matters="Companies earning ROCE comfortably higher than their cost of capital (e.g. > 15-20%) compound shareholder wealth over time.",
                sector_context="Capital-light businesses (IT, depositories) achieve 30-50%+ ROCE, whereas heavy manufacturing averages 12-16%.",
                limitations="Historical ROCE can drop sharply if the company initiates massive debt-funded capex that takes years to commercialize."
            ),
            MetricExplanation(
                metric_name="Debt to Equity Ratio",
                display_value=dte_val,
                meaning="The proportion of borrowed debt funding the company relative to total shareholder equity.",
                why_it_matters="Low debt (under 0.5x) provides safety during economic downturns, whereas high debt (> 1.5x) elevates insolvency risk.",
                sector_context="For Banks and NBFCs, customer deposits are operating liabilities used to fund loans, so industrial D/E is Not Applicable.",
                limitations="Does not reflect off-balance sheet parent corporate guarantees or contingent lease liabilities."
            ),
            MetricExplanation(
                metric_name="Margin of Safety",
                display_value=mos_val,
                meaning="The percentage difference between the modeled intrinsic fair value and the current market price.",
                why_it_matters="A positive margin of safety (> +15%) acts as an investment cushion if future business growth is slower than expected.",
                sector_context="Smallcap stocks experience greater cyclical volatility, requiring a wider margin of safety buffer (20-25%) than bluechips.",
                limitations="Margin of safety is only as reliable as the cash flow and growth assumptions used in the underlying valuation model."
            ),
            MetricExplanation(
                metric_name="Free Cash Flow (FCF)",
                display_value=fcf_val,
                meaning="Cash generated from operations remaining after subtracting capital expenditures (capex) needed to maintain and grow assets.",
                why_it_matters="Accounting profits can be cosmetically inflated via aggressive revenue booking, but Free Cash Flow reflects actual cash available to pay dividends, reduce debt, or reinvest.",
                sector_context="In high-growth capital-intensive industries (e.g., semiconductor or gigafactories), FCF may be temporarily negative during build-out phases.",
                limitations="FCF fluctuates from year to year depending on the timing of major equipment purchases and working capital swings."
            )
        ]

research_decision_engine = ResearchDecisionEngine()
