"""
Phase 2 Functional Modernization Comprehensive Test Suite.
Validates institutional accuracy, universe coverage, event studies, NLP evaluation,
RAG research assistant, navigation cleanup, ML ranking baselines, and backtest friction costs.
"""
import pytest
from fastapi.testclient import TestClient

from bharat_value_ai.main import app
from bharat_value_ai.data.security_master import (
    security_master, coverage_tracker, SecurityStatus, OverallEligibilityStatus
)
from bharat_value_ai.ml.event_study import event_study_engine
from bharat_value_ai.nlp.evaluation import nlp_evaluation_suite
from bharat_value_ai.rag.assistant import rag_assistant
from bharat_value_ai.ml.pipeline import ml_ranking_lab
from bharat_value_ai.ml.backtester import backtester
from bharat_value_ai.core.schemas import BacktestRequest


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------
# PHASE 1: Universe & Data Coverage
# ---------------------------------------------------------

def test_phase1_security_master_and_status_tracking():
    """Verify security master tracks active, suspended, and delisted stocks accurately."""
    active = security_master.get_security("CDSL")
    assert active is not None
    assert active.exchange == "NSE"
    assert active.status == SecurityStatus.ACTIVE
    assert active.isin == "INE736A01011"

    # Suspended / historical delisted stocks for survivorship bias testing
    delisted = security_master.get_security("DHFL_HISTORICAL")
    assert delisted is not None
    assert delisted.status == SecurityStatus.DELISTED
    assert delisted.is_financial is True

    # Unknown stock lookup
    assert security_master.get_security("UNKNOWN_TICKER_999") is None


def test_phase1_coverage_tracker_dimensions_and_guard():
    """Verify coverage dimensions across Quote, History, Fundamentals, and Disclosures."""
    # Active, fully catalogued stock
    rep = coverage_tracker.get_symbol_coverage("CDSL")
    assert rep.symbol == "CDSL"
    assert rep.status == SecurityStatus.ACTIVE
    assert rep.eligibility == OverallEligibilityStatus.COVERED
    assert rep.quote_coverage["status"] in ("COVERED", "PARTIAL")
    assert rep.historical_price_coverage["status"] in ("COVERED", "PARTIAL")
    assert rep.fundamental_coverage["status"] in ("COVERED", "PARTIAL")
    assert rep.news_coverage["status"] in ("COVERED", "SPARSE")

    # Guard method allows eligible stocks
    coverage_tracker.ensure_eligible_for_analysis("CDSL", "valuation")

    # Guard strictly rejects delisted stocks from entering valuation/ranking/backtesting
    with pytest.raises(ValueError) as exc:
        coverage_tracker.ensure_eligible_for_analysis("DHFL_HISTORICAL", "ranking")
    assert "EXCLUDED from analysis" in str(exc.value)
    assert "delisted" in str(exc.value)

    # Summary reports active and excluded counts correctly
    summary = coverage_tracker.get_universe_coverage_summary()
    assert summary["total_registered_securities"] >= 24
    assert summary["total_eligible_active"] >= 22
    assert summary["total_excluded"] >= 2


def test_phase1_universe_coverage_endpoints(client):
    """Test HTTP API endpoints for universe coverage and security master refresh."""
    res = client.get("/api/universe/coverage")
    assert res.status_code == 200
    data = res.json()
    assert "total_registered_securities" in data
    assert data["total_eligible_active"] >= 22

    res_sym = client.get("/api/universe/coverage/CDSL")
    assert res_sym.status_code == 200
    sym_data = res_sym.json()
    assert sym_data["symbol"] == "CDSL"
    assert sym_data["eligibility"] == "COVERED"

    res_refresh = client.post("/api/universe/refresh")
    assert res_refresh.status_code == 200
    ref_data = res_refresh.json()
    assert ref_data["status"] == "SUCCESS"


# ---------------------------------------------------------
# PHASE 2: News-to-Price Events
# ---------------------------------------------------------

def test_phase2_event_study_reaction_windows_and_causality():
    """Verify event study windows, benchmark-adjusted returns, sample size, and non-causal claims."""
    studies = event_study_engine.get_event_studies("CDSL")
    assert len(studies) > 0
    ev = studies[0]

    assert ev.symbol == "CDSL"
    assert ev.event_date is not None
    assert ev.publication_time is not None
    assert ev.retrieval_timestamp is not None
    assert ev.reaction_window_status in ("COMPLETED", "PARTIAL_REACTION", "INSUFFICIENT_HISTORY")

    # Valid returns and volume shock
    assert ev.reaction_1d_pct is not None
    assert ev.benchmark_adjusted_return_1d_pct is not None
    assert ev.volume_shock_ratio is not None
    assert ev.sample_size_days is not None
    assert ev.sample_size_days >= 1

    # Causality integrity
    assert ev.is_causal_claim is False
    disclaimer = getattr(ev, "causality_disclaimer", None) or getattr(ev, "methodology_note", "")
    assert "causal" in disclaimer.lower()


def test_phase2_event_study_missing_symbol_handling():
    """Verify empty/missing event responses for unsupported symbols without crashing."""
    studies = event_study_engine.get_event_studies("UNREGISTERED_TEST_TICKER")
    assert isinstance(studies, list)
    assert len(studies) == 0


# ---------------------------------------------------------
# PHASE 3: Financial NLP Evaluation
# ---------------------------------------------------------

def test_phase3_nlp_evaluation_held_out_benchmark():
    """Evaluate financial NLP pipeline on held-out dataset with calibration and confusion matrix."""
    metrics = nlp_evaluation_suite.evaluate_held_out_benchmark()
    assert metrics.test_set_size == 22
    assert metrics.sentiment_accuracy >= 0.50
    assert metrics.macro_f1 >= 0.40
    assert 0.0 <= metrics.brier_score <= 1.0
    assert 0.0 <= metrics.expected_calibration_error <= 1.0

    # Per-class metrics
    assert "POSITIVE" in metrics.per_class_metrics
    assert "NEGATIVE" in metrics.per_class_metrics
    assert "NEUTRAL" in metrics.per_class_metrics

    # Confusion matrix has positive, negative, neutral
    cm = metrics.confusion_matrix
    assert "POSITIVE" in cm and "NEGATIVE" in cm and "NEUTRAL" in cm

    # Outperformance over naive majority class
    assert metrics.lift_over_majority_baseline >= 0.0


def test_phase3_nlp_evaluation_report_api(client):
    """Verify downloadable evaluation report endpoint returns valid Markdown text."""
    res = client.get("/api/nlp/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["test_set_size"] == 22
    assert "macro_f1" in data

    res_report = client.get("/api/nlp/evaluation/report")
    assert res_report.status_code == 200
    assert "text/markdown" in res_report.headers.get("content-type", "")
    assert "# Financial NLP & FinBERT Rigorous Benchmark Evaluation Report" in res_report.text


# ---------------------------------------------------------
# PHASE 4: RAG Research Assistant
# ---------------------------------------------------------

def test_phase4_rag_evidence_grounding_and_citations():
    """Verify RAG retrieval produces citations with section titles, hashes, and excerpts."""
    res = rag_assistant.query("What are the main growth drivers for CDSL?", symbol="CDSL")
    assert res.symbol == "CDSL"
    assert res.has_sufficient_evidence is True
    assert len(res.citations) > 0

    first_cite = res.citations[0]
    assert first_cite.document_title != ""
    assert first_cite.reporting_period is not None
    assert first_cite.snippet != ""
    assert first_cite.relevance_score > 0.0


def test_phase4_rag_comparative_queries():
    """Verify comparative RAG query across two Indian companies (e.g. CDSL and CAMS)."""
    res = rag_assistant.query("Compare the business models and revenue drivers of CDSL and CAMS")
    assert res.has_sufficient_evidence is True
    assert "CDSL" in res.answer
    assert "CAMS" in res.answer
    assert len(res.citations) >= 2


def test_phase4_rag_refusal_on_missing_evidence():
    """Verify RAG refuses to fabricate data when sources contain no relevant evidence."""
    res = rag_assistant.query("What are the nuclear submarine propulsion revenues for CDSL?", symbol="CDSL")
    assert res.has_sufficient_evidence is False
    assert "insufficient" in res.answer.lower()


# ---------------------------------------------------------
# PHASE 5: Primary Navigation Multi-Agent Removal
# ---------------------------------------------------------

def test_phase5_sidebar_navigation_removes_agents_entry(client):
    """Verify the primary sidebar navigation does not contain the multi-agent workflow."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # Sidebar menu must NOT have data-view="agents"
    # Find sidebar <aside id="sidebar"> block
    sidebar_idx = html.find('<aside id="sidebar">')
    sidebar_end = html.find('</aside>')
    assert sidebar_idx != -1 and sidebar_end != -1
    sidebar_content = html[sidebar_idx:sidebar_end]

    assert 'data-view="agents"' not in sidebar_content
    # Shared research endpoint still accessible
    res_agent = client.get("/api/agents/research/CDSL")
    assert res_agent.status_code == 200


# ---------------------------------------------------------
# PHASE 6: ML Stock Ranking & Baselines
# ---------------------------------------------------------

def test_phase6_ml_ranking_baselines_and_topk_costs():
    """Verify ML ranking pipeline compares against Ridge and Quality baselines with trading costs."""
    res = ml_ranking_lab.train_and_rank(horizon_days=60)
    assert res.horizon_days == 60
    assert len(res.top_ranked) > 0
    assert len(res.bottom_ranked) > 0

    # Baseline comparison metrics
    b_comp = res.baseline_comparison
    assert b_comp is not None
    assert "xgboost_spearman_rho" in b_comp
    assert "ridge_linear_spearman_rho" in b_comp
    assert "heuristic_quality_spearman_rho" in b_comp

    # Top-K simulation with realistic friction costs
    top_k = res.top_k_performance
    assert top_k is not None
    assert top_k["friction_cost_deduction_pct"] > 0.0
    assert top_k["top_quintile_annualized_return_pct"] > 0.0

    # Uncertainty bands
    for stock in res.top_ranked:
        assert "uncertainty_band_pct" in stock
        assert stock["uncertainty_band_pct"] > 0.0

    # Coverage diagnostics
    diag = res.coverage_diagnostics
    assert diag is not None
    assert diag["total_universe_tested"] >= 20
    assert diag["coverage_verification_status"] == "PASSED"


# ---------------------------------------------------------
# PHASE 7: Strategy Backtesting Friction Costs
# ---------------------------------------------------------

def test_phase7_backtest_statutory_friction_and_sortino():
    """Verify Indian statutory charges (brokerage, STT 0.1%, GST 18%, slippage) and Sortino ratio."""
    req = BacktestRequest(
        strategy_name="Quality_Value_Momentum",
        start_date="2021-01-01",
        end_date="2024-01-01",
        include_costs=True,
        brokerage_pct=0.0005,
        stt_pct=0.001,       # 0.1% STT on equity delivery
        slippage_pct=0.0005
    )
    res = backtester.run_backtest(req)

    assert res.cagr_pct > 0.0
    assert res.sharpe_ratio != 0.0
    assert res.sortino_ratio is not None
    assert res.sortino_ratio != 0.0
    assert res.max_drawdown_pct >= 0.0
    assert res.cost_drag_pct > 0.0

    # Equity curve has chronological points
    assert len(res.equity_curve) > 10
    first_pt = res.equity_curve[0]
    assert first_pt["strategy"] == 100.0
    assert first_pt["benchmark"] == 100.0
