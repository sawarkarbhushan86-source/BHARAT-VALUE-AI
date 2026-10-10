"""Deterministic Fair-Value Engine (DCF, Relative Valuation, Sensitivity Matrix, and Scenarios)."""
from typing import Dict, Any, List, Tuple
import numpy as np

from bharat_value_ai.core.schemas import DCFParameters, ValuationResult
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.data.market_provider import market_provider

class FairValueEngine:
    """
    Computes rigorous, mathematically sound, deterministic valuations.
    Does NOT hallucinate fair values using LLM prompts.
    """

    @staticmethod
    def calculate_dcf(
        base_fcf: float,
        shares_outstanding_cr: float,
        net_debt_cr: float,
        params: DCFParameters
    ) -> Tuple[float, List[float], float]:
        """
        Discounted Cash Flow Valuation.
        Returns: (per_share_value, discounted_cash_flows, terminal_value)
        """
        if params.discount_rate_wacc <= params.terminal_growth_rate:
            raise ValueError("Discount rate (WACC) must be strictly greater than terminal growth rate.")

        fcf_projections = []
        discounted_fcfs = []
        current_fcf = max(10.0, base_fcf) # Floor to positive cash flow baseline

        # Explicit forecast horizon
        for yr in range(1, params.forecast_years + 1):
            projected_fcf = current_fcf * ((1.0 + params.revenue_growth_rate) ** yr)
            discount_factor = (1.0 + params.discount_rate_wacc) ** yr
            pv_fcf = projected_fcf / discount_factor
            fcf_projections.append(projected_fcf)
            discounted_fcfs.append(pv_fcf)

        # Terminal Value via Gordon Growth Model
        terminal_fcf = fcf_projections[-1] * (1.0 + params.terminal_growth_rate)
        terminal_value = terminal_fcf / (params.discount_rate_wacc - params.terminal_growth_rate)
        pv_terminal_value = terminal_value / ((1.0 + params.discount_rate_wacc) ** params.forecast_years)

        # Enterprise Value & Equity Value
        enterprise_value = sum(discounted_fcfs) + pv_terminal_value
        equity_value = enterprise_value - net_debt_cr

        # Per share value in INR
        per_share_value = equity_value / shares_outstanding_cr if shares_outstanding_cr > 0 else 0.0
        return max(0.0, per_share_value), discounted_fcfs, pv_terminal_value

    @staticmethod
    def generate_sensitivity_matrix(
        base_fcf: float,
        shares_cr: float,
        net_debt_cr: float,
        growth_rate: float,
        forecast_years: int
    ) -> Tuple[List[List[float]], List[float], List[float]]:
        """
        Calculates fair values across varying WACCs and Terminal Growth rates.
        """
        wacc_range = [0.10, 0.11, 0.12, 0.13, 0.14]
        g_range = [0.03, 0.04, 0.05, 0.06]

        matrix = []
        for w in wacc_range:
            row = []
            for g in g_range:
                if w <= g:
                    row.append(0.0)
                    continue
                params = DCFParameters(
                    symbol="",
                    forecast_years=forecast_years,
                    revenue_growth_rate=growth_rate,
                    discount_rate_wacc=w,
                    terminal_growth_rate=g
                )
                val, _, _ = FairValueEngine.calculate_dcf(base_fcf, shares_cr, net_debt_cr, params)
                row.append(round(val, 2))
            matrix.append(row)

        return matrix, [round(w * 100, 1) for w in wacc_range], [round(g * 100, 1) for g in g_range]

    def evaluate_valuation(self, symbol: str, custom_params: DCFParameters = None) -> ValuationResult:
        """Run comprehensive valuation suite combining DCF, multiples, scenarios, and margin of safety."""
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        quote = market_provider.get_quote(sym)
        current_price = quote.get("price", 100.0)

        fundamentals = fundamentals_engine.get_company_fundamentals(sym)
        net_profit = fundamentals.get("net_profit", 100.0)
        ebitda = fundamentals.get("operating_profit", 150.0)
        debt = fundamentals.get("total_debt", 0.0)
        cash = fundamentals.get("cash_and_equivalents", 50.0)
        net_debt = debt - cash
        fcf = fundamentals.get("free_cash_flow", net_profit * 0.8)
        eps = fundamentals.get("eps", 10.0)

        # Estimate shares outstanding (Net Profit Cr / EPS)
        shares_cr = (net_profit / eps) if eps > 0 else 10.0
        if shares_cr <= 0:
            shares_cr = 10.0

        if custom_params is None:
            # Calibrate default growth rate from historical 3Y CAGR
            hist_cagr = fundamentals.get("revenue_growth_3y_cagr", 15.0) / 100.0
            growth = max(0.05, min(0.35, hist_cagr * 0.85)) # conservative moderation
            custom_params = DCFParameters(
                symbol=sym,
                forecast_years=5,
                revenue_growth_rate=round(growth, 3),
                discount_rate_wacc=0.12,
                terminal_growth_rate=0.05
            )

        # 1. Base DCF
        dcf_value, _, _ = self.calculate_dcf(fcf, shares_cr, net_debt, custom_params)

        # 2. Relative Multiple Valuations
        pe_fair_value = eps * 25.0 # Benchmark Indian Smallcap Median P/E
        ev_ebitda_fair_value = max(0.0, ((ebitda * 15.0) - net_debt) / shares_cr)

        # 3. Composite Fair Value (Weighted Average)
        composite = (dcf_value * 0.50) + (pe_fair_value * 0.30) + (ev_ebitda_fair_value * 0.20)

        # 4. Scenarios
        # Bear Case: growth reduced by 30%, WACC + 1.5%
        bear_params = DCFParameters(
            symbol=sym,
            forecast_years=custom_params.forecast_years,
            revenue_growth_rate=custom_params.revenue_growth_rate * 0.7,
            discount_rate_wacc=custom_params.discount_rate_wacc + 0.015,
            terminal_growth_rate=0.04
        )
        bear_val, _, _ = self.calculate_dcf(fcf, shares_cr, net_debt, bear_params)

        # Bull Case: growth increased by 25%, WACC - 1.0%
        bull_params = DCFParameters(
            symbol=sym,
            forecast_years=custom_params.forecast_years,
            revenue_growth_rate=custom_params.revenue_growth_rate * 1.25,
            discount_rate_wacc=max(0.09, custom_params.discount_rate_wacc - 0.01),
            terminal_growth_rate=0.06
        )
        bull_val, _, _ = self.calculate_dcf(fcf, shares_cr, net_debt, bull_params)

        # 5. Margin of Safety
        mos_pct = ((composite - current_price) / composite) * 100.0 if composite > 0 else 0.0

        if mos_pct > 15.0:
            status = "UNDERVALUED"
        elif mos_pct < -15.0:
            status = "OVERVALUED"
        else:
            status = "FAIRLY_VALUED"

        # Sensitivity Matrix
        matrix, wacc_labels, g_labels = self.generate_sensitivity_matrix(
            fcf, shares_cr, net_debt, custom_params.revenue_growth_rate, custom_params.forecast_years
        )

        return ValuationResult(
            symbol=sym,
            current_price=round(current_price, 2),
            dcf_fair_value=round(dcf_value, 2),
            pe_fair_value=round(pe_fair_value, 2),
            ev_ebitda_fair_value=round(ev_ebitda_fair_value, 2),
            composite_fair_value=round(composite, 2),
            margin_of_safety_pct=round(mos_pct, 2),
            bear_case_value=round(bear_val, 2),
            base_case_value=round(composite, 2),
            bull_case_value=round(bull_val, 2),
            valuation_status=status,
            assumptions={
                "wacc": custom_params.discount_rate_wacc,
                "terminal_growth": custom_params.terminal_growth_rate,
                "revenue_growth": custom_params.revenue_growth_rate,
                "shares_outstanding_cr": round(shares_cr, 2),
                "net_debt_cr": round(net_debt, 2),
                "base_fcf_cr": round(fcf, 2)
            },
            sensitivity_matrix=matrix,
            sensitivity_wacc_labels=wacc_labels,
            sensitivity_growth_labels=g_labels
        )

fair_value_engine = FairValueEngine()
