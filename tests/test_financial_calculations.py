"""Unit tests for financial calculations, DCF, DuPont, and Solvency."""
import pytest
from bharat_value_ai.core.schemas import DCFParameters
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.analysis.fair_value import fair_value_engine
from bharat_value_ai.analysis.risk_governance import risk_engine

def test_dupont_3_stage_calculation():
    sample_fund = {
        "symbol": "TEST_CO",
        "revenue": 1000.0,
        "net_profit": 150.0,
        "total_assets": 2000.0,
        "total_equity": 1000.0
    }
    dupont = fundamentals_engine.compute_dupont_3_stage(sample_fund)
    assert dupont["roe_pct"] == 15.0
    assert dupont["net_profit_margin_pct"] == 15.0
    assert dupont["asset_turnover"] == 0.5
    assert dupont["equity_multiplier"] == 2.0
    assert "roe_pct" in dupont

def test_altman_z_score_calculation():
    # Healthy company
    z_healthy = fundamentals_engine.compute_altman_z_score(
        working_cap=500, retained_earnings=800, ebit=300,
        market_cap=4000, total_liabilities=1000, sales=2000, total_assets=2500
    )
    assert z_healthy > 2.99 # Safe zone

    # Distressed company
    z_distressed = fundamentals_engine.compute_altman_z_score(
        working_cap=-200, retained_earnings=-500, ebit=-50,
        market_cap=100, total_liabilities=2000, sales=500, total_assets=1500
    )
    assert z_distressed < 1.81 # Distress zone

def test_dcf_valuation_calculation():
    params = DCFParameters(
        symbol="CDSL",
        forecast_years=5,
        revenue_growth_rate=0.15,
        discount_rate_wacc=0.12,
        terminal_growth_rate=0.05
    )
    per_share_val, discounted_fcfs, terminal_val = fair_value_engine.calculate_dcf(
        base_fcf=385.0,
        shares_outstanding_cr=20.9,
        net_debt_cr=-850.0, # Net cash
        params=params
    )
    assert per_share_val > 0
    assert len(discounted_fcfs) == 5
    assert terminal_val > 0

def test_dcf_invalid_wacc_raises_error():
    # WACC <= terminal growth rate must raise ValueError in calculate_dcf
    invalid_params = DCFParameters(
        symbol="TEST",
        forecast_years=5,
        revenue_growth_rate=0.10,
        discount_rate_wacc=0.07,
        terminal_growth_rate=0.07
    )
    with pytest.raises(ValueError, match="strictly greater"):
        fair_value_engine.calculate_dcf(
            base_fcf=100.0,
            shares_outstanding_cr=10.0,
            net_debt_cr=0.0,
            params=invalid_params
        )

def test_full_valuation_suite():
    res = fair_value_engine.evaluate_valuation("CDSL")
    assert res.current_price > 0
    assert res.dcf_fair_value > 0
    assert res.composite_fair_value > 0
    assert res.bear_case_value < res.bull_case_value
    assert len(res.sensitivity_matrix) == 5
    assert res.valuation_status in ["UNDERVALUED", "FAIRLY_VALUED", "OVERVALUED"]
