"""Business Quality, Long-Term Compounding, and Multibagger Evaluation Framework."""
from typing import Dict, Any, List
from bharat_value_ai.core.schemas import QualityScoreResponse
from bharat_value_ai.analysis.fundamentals import fundamentals_engine

class BusinessQualityEngine:
    """
    Evaluates institutional quality and long-term compounding potential over a 5-10 year horizon.
    Calculates transparent scores across 5 pillars:
    1. Business Quality & Moat
    2. Financial Strength & Capital Efficiency
    3. Growth Runway & Market Opportunity
    4. Valuation Attractiveness
    5. Governance & Balance Sheet Resilience
    """

    def evaluate_company(self, symbol: str) -> QualityScoreResponse:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        fund = fundamentals_engine.get_company_fundamentals(sym)

        # 1. Business Quality & Moat (Max 100)
        # Driven by Gross Margin, Net Margin, Operating Margin stability
        gm = fund.get("gross_margin_pct", 30.0)
        npm = fund.get("net_margin_pct", 10.0)
        ccc = fund.get("cash_conversion_cycle", 60.0)

        moat_score = 0.0
        if gm > 50.0: moat_score += 35.0
        elif gm > 30.0: moat_score += 25.0
        else: moat_score += 15.0

        if npm > 25.0: moat_score += 35.0
        elif npm > 12.0: moat_score += 25.0
        elif npm > 6.0: moat_score += 15.0
        else: moat_score += 5.0

        if ccc < 30.0: moat_score += 30.0 # Negative or low working capital cycle
        elif ccc < 60.0: moat_score += 20.0
        else: moat_score += 10.0

        # 2. Financial Strength (Max 100)
        # ROCE, ROE, Debt/Equity, Interest Coverage
        roce = fund.get("roce_pct", 15.0)
        roe = fund.get("roe_pct", 15.0)
        dte = fund.get("debt_to_equity", 0.5)
        ic = fund.get("interest_coverage", 5.0)

        fin_score = 0.0
        if roce > 25.0: fin_score += 30.0
        elif roce > 18.0: fin_score += 22.0
        else: fin_score += 12.0

        if roe > 20.0: fin_score += 25.0
        elif roe > 15.0: fin_score += 18.0
        else: fin_score += 10.0

        if dte < 0.1: fin_score += 25.0 # Virtually debt-free
        elif dte < 0.5: fin_score += 18.0
        elif dte < 1.0: fin_score += 10.0
        else: fin_score += 2.0

        if ic > 15.0: fin_score += 20.0
        elif ic > 5.0: fin_score += 12.0
        else: fin_score += 4.0

        # 3. Growth Potential (Max 100)
        # 3Y Sales CAGR, 3Y PAT CAGR, FCF Conversion
        sales_cagr = fund.get("revenue_growth_3y_cagr", 12.0)
        pat_cagr = fund.get("profit_growth_3y_cagr", 15.0)
        fcf = fund.get("free_cash_flow", 50.0)
        pat = fund.get("net_profit", 100.0)
        fcf_conv = (fcf / pat) if pat > 0 else 0.5

        growth_score = 0.0
        if sales_cagr > 25.0: growth_score += 35.0
        elif sales_cagr > 15.0: growth_score += 25.0
        else: growth_score += 12.0

        if pat_cagr > 25.0: growth_score += 35.0
        elif pat_cagr > 15.0: growth_score += 25.0
        else: growth_score += 12.0

        if fcf_conv > 0.7: growth_score += 30.0
        elif fcf_conv > 0.4: growth_score += 18.0
        else: growth_score += 8.0

        # 4. Valuation Attractiveness (Max 100)
        pe = fund.get("pe_ratio", 30.0)
        peg = (pe / pat_cagr) if pat_cagr > 5.0 else 3.0

        val_score = 0.0
        if peg < 1.0: val_score += 40.0
        elif peg < 1.8: val_score += 25.0
        else: val_score += 10.0

        if pe < 20.0: val_score += 35.0
        elif pe < 35.0: val_score += 22.0
        elif pe < 60.0: val_score += 10.0
        else: val_score += 2.0

        val_score += 25.0 # Baseline multiples credit

        # 5. Governance & Solvency (Max 100)
        pledge = fund.get("promoter_pledge_pct", 0.0)
        promoter = fund.get("promoter_holding_pct", 50.0)
        altman = fund.get("altman_z_score", 3.0)

        gov_score = 0.0
        if pledge == 0.0: gov_score += 40.0
        elif pledge < 10.0: gov_score += 25.0
        elif pledge < 25.0: gov_score += 10.0
        else: gov_score += 0.0 # Severe penalty for high pledge

        if promoter > 50.0 or promoter == 0.0: # 0.0 for professionally run / institutional board like CAMS, CDSL
            gov_score += 30.0
        elif promoter > 30.0:
            gov_score += 20.0
        else:
            gov_score += 10.0

        if altman > 3.0: gov_score += 30.0 # Safe Zone
        elif altman > 1.8: gov_score += 15.0 # Grey Zone
        else: gov_score += 0.0 # Distress Zone

        # Composite Weighted Score
        # Moat 25%, Financials 25%, Growth 20%, Governance 20%, Valuation 10%
        composite = (
            (moat_score * 0.25) +
            (fin_score * 0.25) +
            (growth_score * 0.20) +
            (gov_score * 0.20) +
            (val_score * 0.10)
        )

        if composite >= 80.0:
            tier = "High Conviction Compounder"
        elif composite >= 68.0:
            tier = "Selective Growth Compounder"
        elif composite >= 50.0:
            tier = "Average Quality / Cyclical"
        elif composite >= 35.0:
            tier = "Speculative / Turnaround"
        else:
            tier = "High Risk / Capital Destructive"

        return QualityScoreResponse(
            symbol=sym,
            composite_score=round(composite, 1),
            business_quality_score=round(moat_score, 1),
            financial_strength_score=round(fin_score, 1),
            growth_potential_score=round(growth_score, 1),
            valuation_attractiveness_score=round(val_score, 1),
            governance_score=round(gov_score, 1),
            multibagger_potential_tier=tier,
            factor_breakdown={
                "gross_margin": gm,
                "net_profit_margin": npm,
                "roce": roce,
                "roe": roe,
                "debt_to_equity": dte,
                "sales_growth_3y": sales_cagr,
                "profit_growth_3y": pat_cagr,
                "pe_ratio": pe,
                "promoter_pledge": pledge,
                "altman_z_score": altman
            },
            limitations=[
                "Score reflects reported historical data and audited financials, not future certainty.",
                "Smallcap earnings can experience sharp cyclicality during macro tightening.",
                "Turnaround companies may exhibit elevated historical multiples that normalize later."
            ]
        )

quality_engine = BusinessQualityEngine()
