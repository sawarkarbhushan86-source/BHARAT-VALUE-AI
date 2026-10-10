"""Unit tests for ML ranking, walk-forward backtesting, and event studies."""
from bharat_value_ai.core.schemas import BacktestRequest
from bharat_value_ai.ml.pipeline import ml_ranking_lab
from bharat_value_ai.ml.backtester import backtester
from bharat_value_ai.ml.event_study import event_study_engine

def test_ml_stock_ranking_pipeline():
    res = ml_ranking_lab.train_and_rank(horizon_days=60)
    assert res.horizon_days == 60
    assert len(res.top_ranked) > 0
    assert len(res.bottom_ranked) > 0
    assert len(res.feature_importance) > 0
    assert "roce_pct" in res.feature_importance
    # Top ranked stock score should exceed bottom ranked stock score
    assert res.top_ranked[0]["rank_score"] >= res.bottom_ranked[-1]["rank_score"]

def test_walk_forward_backtest_with_transaction_costs():
    req = BacktestRequest(
        strategy_name="Quality_Value_Momentum",
        start_date="2021-01-01",
        end_date="2024-01-01",
        include_costs=True,
        brokerage_pct=0.0005,
        stt_pct=0.001,
        slippage_pct=0.0005
    )
    res = backtester.run_backtest(req)
    assert res.cagr_pct != 0.0
    assert res.sharpe_ratio != 0.0
    assert res.max_drawdown_pct >= 0.0
    assert res.cost_drag_pct > 0.0 # Transaction costs must produce drag
    assert len(res.equity_curve) > 10
    assert res.equity_curve[0]["strategy"] == 100.0

def test_event_study_engine():
    studies = event_study_engine.get_event_studies("CDSL")
    assert len(studies) > 0
    assert studies[0].symbol == "CDSL"
    assert studies[0].reaction_1d_pct is not None
    assert studies[0].volume_shock_ratio is not None
