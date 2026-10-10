"""Risk and Corporate Governance Intelligence Engine."""
import datetime
from typing import Dict, Any, List
from bharat_value_ai.core.schemas import RiskFlagResponse
from bharat_value_ai.analysis.fundamentals import fundamentals_engine

class RiskGovernanceEngine:
    """Detects forensic red flags and balance-sheet vulnerabilities with evidentiary trails."""

    def evaluate_risks(self, symbol: str) -> List[RiskFlagResponse]:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        fund = fundamentals_engine.get_company_fundamentals(sym)
        flags: List[RiskFlagResponse] = []
        now = datetime.datetime.now(datetime.timezone.utc)
        idx_counter = 1

        # Check 1: High Promoter Pledge (> 25%)
        pledge_pct = fund.get("promoter_pledge_pct", 0.0)
        if pledge_pct > 25.0:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="HIGH_PROMOTER_PLEDGE",
                category="Governance",
                severity="CRITICAL",
                title="High Promoter Share Encumbrance",
                description=f"Promoters have pledged {pledge_pct}% of their holding. High pledge poses margin-call liquidation risk during market corrections.",
                supporting_data={"pledge_pct": pledge_pct, "threshold": 25.0},
                evidence_source="Shareholding Pattern Filing (SEBI Clause 31)",
                confidence=0.98,
                date_identified=now
            ))
            idx_counter += 1
        elif pledge_pct > 10.0:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="MODERATE_PROMOTER_PLEDGE",
                category="Governance",
                severity="MEDIUM",
                title="Moderate Promoter Pledging",
                description=f"Promoter pledge stands at {pledge_pct}%. Requires monitoring for any incremental encumbrance.",
                supporting_data={"pledge_pct": pledge_pct, "threshold": 10.0},
                evidence_source="Shareholding Pattern Filing",
                confidence=0.95,
                date_identified=now
            ))
            idx_counter += 1

        # Check 2: Low Interest Coverage (< 2.5x)
        ic = fund.get("interest_coverage", 10.0)
        debt = fund.get("total_debt", 0.0)
        if debt > 50.0 and ic < 2.5:
            severity = "HIGH" if ic < 1.5 else "MEDIUM"
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="LOW_INTEREST_COVERAGE",
                category="Leverage",
                severity=severity,
                title="Weak Debt Servicing Capacity",
                description=f"Interest coverage ratio is {ic}x (below the safety benchmark of 2.5x). Vulnerable to interest rate hikes and operating margin contraction.",
                supporting_data={"interest_coverage": ic, "total_debt_cr": debt},
                evidence_source="Audited Profit & Loss Statement (Finance Costs)",
                confidence=0.95,
                date_identified=now
            ))
            idx_counter += 1

        # Check 3: Elevated Debt to Equity (> 1.5x)
        dte = fund.get("debt_to_equity", 0.2)
        if dte > 1.5:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="ELEVATED_LEVERAGE",
                category="Leverage",
                severity="HIGH",
                title="High Financial Leverage",
                description=f"Debt-to-equity ratio of {dte} exceeds conservative thresholds, increasing bankruptcy and solvency risks in cyclical downturns.",
                supporting_data={"debt_to_equity": dte, "total_debt_cr": debt},
                evidence_source="Audited Balance Sheet (Non-Current Borrowings)",
                confidence=0.95,
                date_identified=now
            ))
            idx_counter += 1

        # Check 4: Cash Flow Divergence (OCF vs Net Profit)
        ocf = fund.get("operating_cash_flow", 100.0)
        pat = fund.get("net_profit", 100.0)
        if pat > 50.0 and ocf < (pat * 0.40):
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="CASH_FLOW_PAT_DIVERGENCE",
                category="CashFlow",
                severity="HIGH",
                title="Poor Cash Flow Conversion from Profits",
                description=f"Operating cash flow (₹{ocf} Cr) is significantly below reported Net Profit (₹{pat} Cr). Indicates potential aggressive revenue recognition or ballooning receivables.",
                supporting_data={"operating_cash_flow_cr": ocf, "net_profit_cr": pat, "ratio": round(ocf / pat, 2)},
                evidence_source="Cash Flow Statement vs Profit & Loss",
                confidence=0.92,
                date_identified=now
            ))
            idx_counter += 1

        # Check 5: Negative Free Cash Flow with Ongoing Debt Expansion
        fcf = fund.get("free_cash_flow", 50.0)
        if fcf < -50.0 and debt > 200.0:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="NEGATIVE_FREE_CASH_FLOW",
                category="CashFlow",
                severity="MEDIUM",
                title="Sustained Negative Free Cash Flow",
                description=f"Free cash flow is negative (₹{fcf} Cr) due to heavy capital expenditure or working capital blockage, funded via external borrowings.",
                supporting_data={"free_cash_flow_cr": fcf, "total_debt_cr": debt},
                evidence_source="Cash Flow Statement (Capex Outflows)",
                confidence=0.90,
                date_identified=now
            ))
            idx_counter += 1

        # Check 6: Solvency Distress via Altman Z-Score (< 1.81)
        z_score = fund.get("altman_z_score", 3.5)
        if z_score < 1.81:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="ALTMAN_Z_DISTRESS",
                category="Solvency",
                severity="CRITICAL",
                title="Altman Z-Score in Financial Distress Zone",
                description=f"Altman Z-Score is {z_score} (distress boundary < 1.81). Indicates elevated probability of financial stress over the next 24 months.",
                supporting_data={"altman_z_score": z_score, "distress_boundary": 1.81},
                evidence_source="Multi-Factor Balance Sheet Solvency Model",
                confidence=0.94,
                date_identified=now
            ))
            idx_counter += 1
        elif z_score < 2.99:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="ALTMAN_Z_GREY_ZONE",
                category="Solvency",
                severity="LOW",
                title="Altman Z-Score in Grey Zone",
                description=f"Altman Z-Score is {z_score} (between 1.81 and 2.99). Solvency is adequate but warrants regular working-capital monitoring.",
                supporting_data={"altman_z_score": z_score},
                evidence_source="Multi-Factor Solvency Model",
                confidence=0.90,
                date_identified=now
            ))
            idx_counter += 1

        # Check 7: Extreme Valuation Stretch
        pe = fund.get("pe_ratio", 25.0)
        rev_growth = fund.get("revenue_growth_3y_cagr", 15.0)
        if pe > 80.0 and rev_growth < 15.0:
            flags.append(RiskFlagResponse(
                id=idx_counter,
                symbol=sym,
                flag_code="VALUATION_GROWTH_MISMATCH",
                category="Valuation",
                severity="MEDIUM",
                title="Excessive Valuation Multiple vs Growth Rate",
                description=f"Trading at an elevated P/E of {pe}x despite modest 3-year revenue growth of {rev_growth}%. Asymmetric downside if quarterly results miss consensus expectations.",
                supporting_data={"pe_ratio": pe, "revenue_growth_3y": rev_growth},
                evidence_source="Market Price vs Financial Results",
                confidence=0.88,
                date_identified=now
            ))
            idx_counter += 1

        return flags

risk_engine = RiskGovernanceEngine()
