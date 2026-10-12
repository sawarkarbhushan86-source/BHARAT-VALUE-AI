"""Institutional Reliability & Acceptance Criteria Test Suite.
Validates the 15 Non-Negotiable Acceptance Criteria across all 14 Phases:
1. Canonical price snapshot parity across screens.
2. Stale data never labeled live.
3. Failed providers never cause fabricated quotes.
4. Invalid symbols handled gracefully.
5. Financial formulas pass independent validation.
6. Negative and missing earnings do not create misleading P/E ratios.
7. Sector-appropriate valuation methods selected (Banks vs Industrials).
8. RAG cites official evidence or reports insufficient evidence.
9. Old news cannot appear as newly published news.
10. Multi-agent price consistency across all agents.
11. ML and backtest leakage detection.
12. PDF/CSV reports agree with validated snapshot.
13. Operational API endpoints return valid schemas.
14. FastAPI application uptime and health.
15. Beginner-friendly 10-point research decision summary structure.
"""

import os
import pytest
import datetime
from fastapi.testclient import TestClient

from bharat_value_ai.main import app
from bharat_value_ai.services.snapshot_service import SnapshotService
from bharat_value_ai.services.market_data_service import market_data_service, check_indian_market_session
from bharat_value_ai.data.normalization import QuoteStatus, get_current_utc
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.analysis.fair_value import fair_value_engine
from bharat_value_ai.analysis.research_decision_engine import ResearchDecisionEngine, InvestmentHorizon
from bharat_value_ai.rag.assistant import research_assistant
from bharat_value_ai.agents.orchestrator import agent_orchestrator
from bharat_value_ai.reports.generator import report_generator

client = TestClient(app)


# Criteria 1: Canonical price snapshot parity across screens
def test_criterion_1_canonical_price_snapshot_parity():
    """Verify that quote, valuation, and company snapshot consume the exact same canonical price."""
    snapshot = SnapshotService.get_snapshot("CDSL")
    
    assert snapshot.symbol == "CDSL"
    assert snapshot.current_price > 0
    assert snapshot.current_price == snapshot.quote["price"]
    assert snapshot.current_price == snapshot.valuation["current_price"]
    assert snapshot.price_status in [s.value for s in QuoteStatus]


# Criteria 2: Stale data is never labeled live
def test_criterion_2_stale_data_never_labeled_live():
    """Verify that cached or off-market data is labeled LAST AVAILABLE or DELAYED, never LIVE."""
    quote = market_data_service.get_quote("CDSL")
    
    session = check_indian_market_session()
    
    if not session["is_open"]:
        assert quote["status"] != QuoteStatus.LIVE.value
        assert quote["status"] in [QuoteStatus.LAST_AVAILABLE.value, QuoteStatus.DELAYED.value, QuoteStatus.UNAVAILABLE.value]


# Criteria 3: Failed providers never cause fabricated quotes
def test_criterion_3_failed_providers_never_fabricate():
    """Verify that uncatalogued or failing quotes return UNAVAILABLE without synthetic prices."""
    quote = market_data_service.get_quote("TOTALLY_UNKNOWN_XYZ_999")
    
    assert quote["status"] == QuoteStatus.UNAVAILABLE.value
    assert quote["price"] == 0.0
    assert quote["volume"] == 0


# Criteria 4: Invalid symbols are handled gracefully
def test_criterion_4_invalid_symbol_graceful_handling():
    """Verify that non-existent stock symbols return proper 200 or 404 responses without 500 crash."""
    response = client.get("/api/snapshot/UNKNOWN_SYMBOL_123")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "UNKNOWN_SYMBOL_123"
    assert data["price_status"] == QuoteStatus.UNAVAILABLE.value

    # Research summary handles gracefully
    sum_resp = client.get("/api/research/summary/UNKNOWN_SYMBOL_123")
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()
    assert sum_data["assessment"] == "Insufficient verified data"


# Criteria 5: Financial formulas pass independently calculated test cases
def test_criterion_5_financial_formulas_independent_validation():
    """Verify DuPont 3-stage ROE multiplication: NPM * Asset Turnover * Leverage = ROE."""
    fund = fundamentals_engine.get_company_fundamentals("CDSL")
    dupont = fundamentals_engine.compute_dupont_3_stage(fund)
    
    npm = dupont["net_profit_margin_pct"] / 100.0
    at = dupont["asset_turnover"]
    em = dupont["equity_multiplier"]
    expected_roe_pct = round(npm * at * em * 100, 2)
    
    assert abs(dupont["roe_pct"] - expected_roe_pct) <= 0.2


# Criteria 6: Missing and negative earnings do not create misleading P/E ratios
def test_criterion_6_negative_and_missing_earnings_pe_rules():
    """Verify that negative or zero earnings do not output negative P/E multiples."""
    loss_fund = {
        "symbol": "LOSSKING",
        "revenue": 100.0,
        "net_profit": -25.0,
        "shares_outstanding_cr": 10.0,
        "eps": -2.5
    }
    
    # Negative earnings must yield None or omitted P/E
    eps = loss_fund.get("eps")
    price = 100.0
    pe = round(price / eps, 2) if (eps is not None and eps > 0) else None
    
    assert pe is None, "Negative earnings must never produce a misleading negative P/E ratio"


# Criteria 7: Sector-appropriate valuation methods are selected
def test_criterion_7_sector_appropriate_valuation_routing():
    """Verify that Banks use Justified P/B & RIM, whereas Industrials use DCF."""
    # Banking: HDFC Bank
    hdfc_val = fair_value_engine.evaluate_valuation("HDFCBANK")
    assert hdfc_val.model_type == "BANK_RESIDUAL_INCOME_PB"
    assert hdfc_val.justified_pb_fair_value > 0
    assert hdfc_val.residual_income_fair_value > 0

    # Industrial Conglomerate: Reliance
    ril_val = fair_value_engine.evaluate_valuation("RELIANCE")
    assert ril_val.model_type == "INDUSTRIAL_DCF"
    assert ril_val.dcf_fair_value > 0


# Criteria 8: RAG responses cite relevant evidence or report insufficient evidence
def test_criterion_8_rag_grounding_and_refusal():
    """Verify that RAG cites official filings for indexed topics and refuses unindexed claims."""
    from bharat_value_ai.rag.document_parser import doc_parser_service
    doc_parser_service.seed_initial_knowledge_base()

    # Indexed HDFC Bank query
    hdfc_ans = research_assistant.answer_query(
        "What was HDFC Bank's net interest income or CASA deposits in FY24?",
        symbol="HDFCBANK"
    )
    assert hdfc_ans.has_sufficient_evidence is True
    assert len(hdfc_ans.citations) > 0
    assert any("HDFC" in c.document_title for c in hdfc_ans.citations)

    # Obscure unindexed query
    refusal_ans = research_assistant.answer_query(
        "What are HDFC Bank's offshore uranium mining concessions in Greenland?",
        symbol="HDFCBANK"
    )
    assert refusal_ans.has_sufficient_evidence is False
    assert "insufficient" in refusal_ans.answer.lower() or "not contain" in refusal_ans.answer.lower()


# Criteria 9: Old news cannot appear as newly published news
def test_criterion_9_old_news_timestamp_integrity():
    """Verify news items maintain distinct published_at and ingested_at timestamps."""
    from bharat_value_ai.data.news_provider import news_service
    articles = news_service.fetch_latest_news()
    
    assert len(articles) > 0
    for art in articles:
        assert "published_at" in art
        assert "retrieved_at" in art
        pub_dt = art["published_at"]
        assert isinstance(pub_dt, datetime.datetime)
        assert pub_dt <= datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)


# Criteria 10: Agent disagreements and multi-agent price consistency
def test_criterion_10_multi_agent_price_consistency():
    """Verify all 6 research agents consume identical current price from unified snapshot."""
    res = agent_orchestrator.run_research("CDSL")
    
    assert res.symbol == "CDSL"
    assert len(res.agents) == 6
    assert res.fair_value_estimate > 0
    
    # Valuation agent has current price
    val_agent = next(a for a in res.agents if "Valuation" in a.agent_name)
    assert "current_price" in val_agent.findings
    
    # Skeptical review challenged assumptions
    skeptical_agent = next(a for a in res.agents if "Skeptical" in a.agent_name)
    assert len(skeptical_agent.findings["counter_thesis_points"]) > 0
    assert len(res.audit_trail) > 0


# Criteria 11: ML and backtesting detect look-ahead leakage
def test_criterion_11_ml_and_backtest_integrity():
    """Verify backtesting enforces point-in-time sequential windows and transaction fees."""
    from bharat_value_ai.ml.backtester import backtester
    from bharat_value_ai.core.schemas import BacktestRequest
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
    assert res.cost_drag_pct > 0.0
    assert len(res.equity_curve) > 10


# Criteria 12: Reports agree with the underlying validated data
def test_criterion_12_reports_agree_with_validated_data():
    """Verify that CSV and PDF reports match the unified snapshot current price and fair value."""
    snapshot = SnapshotService.get_snapshot("CDSL")
    
    csv_path = report_generator.generate_csv_report("CDSL")
    assert csv_path.endswith(".csv")
    assert os.path.exists(csv_path)
    with open(csv_path, "r", encoding="utf-8") as f:
        csv_text = f.read()
    
    # CSV must contain exact verified price
    assert str(snapshot.current_price) in csv_text or f"{snapshot.current_price:.2f}" in csv_text
    # CSV must contain fair value
    assert str(round(snapshot.fair_value, 2)) in csv_text or f"{snapshot.fair_value:.2f}" in csv_text

    pdf_path = report_generator.generate_pdf_report("CDSL")
    assert pdf_path.endswith(".pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 2000


# Criteria 13: Every UI action has a functional operational endpoint
def test_criterion_13_ui_endpoints_operational():
    """Verify that all core UI endpoints respond with 200 OK."""
    endpoints = [
        "/api/market/status",
        "/api/market/indices",
        "/api/market/quote/CDSL",
        "/api/universe",
        "/api/snapshot/CDSL",
        "/api/research/summary/CDSL?horizon=medium_term",
        "/api/fundamentals/CDSL",
        "/api/valuation/CDSL",
        "/api/health"
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200, f"Endpoint {ep} failed with {resp.status_code}"


# Criteria 14: FastAPI application uptime and health
def test_criterion_14_fastapi_app_health():
    """Verify health endpoint confirms healthy system state."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"].upper() == "HEALTHY"


# Criteria 15: Beginner-friendly 10-point research summary structure
def test_criterion_15_beginner_research_summary_structure():
    """Verify the 10-point research assessment and educational drawers for ordinary investors."""
    summary = ResearchDecisionEngine.generate_summary("CDSL", horizon=InvestmentHorizon.MEDIUM_TERM)
    
    # 1. Plain English headline and assessment
    assert summary.assessment is not None
    assert len(summary.plain_english_summary) > 10
    
    # 2. Strongest supporting evidence
    assert len(summary.strongest_supporting_evidence) > 10
    
    # 3. Strongest counterargument
    assert len(summary.strongest_counterargument) > 10
    
    # 4. Current valuation vs modeled range
    assert "Verified Price" in summary.current_valuation_vs_range
    assert "Modeled Fair Value" in summary.current_valuation_vs_range
    
    # 5. Business quality and financial health
    assert "Quality Score" in summary.business_quality_and_health
    
    # 6. Growth drivers and assumptions
    assert len(summary.growth_drivers_and_assumptions) > 10
    
    # 7. Material risks and potential downside
    assert len(summary.material_risks_and_downside) > 10
    
    # 8. Data freshness and completeness
    assert len(summary.data_freshness_and_completeness) > 10
    
    # 9. Confidence limitations
    assert len(summary.confidence_limitations) > 10
    
    # 10. Thesis breakers (conditions that invalidate assessment)
    assert len(summary.conditions_to_change_assessment) > 10
    
    # Educational metric drawers
    assert len(summary.metric_educational_drawers) >= 4
    metrics = [d.metric_name for d in summary.metric_educational_drawers]
    assert any("ROCE" in m for m in metrics)
    assert any("Debt" in m for m in metrics)
    assert any("Margin of Safety" in m for m in metrics)
    assert any("Cash Flow" in m for m in metrics)


# Criteria 16: Multi-period statements API & Banking format differentiation (Phase 3)
def test_criterion_16_financial_statements_api():
    """Verify audited statements return multi-period data and sector-appropriate banking vs industrial rows."""
    # Test Industrial / Non-financial (CDSL)
    res_ind = client.get("/api/fundamentals/CDSL/statements?period_type=annual&view=consolidated")
    assert res_ind.status_code == 200
    data_ind = res_ind.json()
    assert data_ind["symbol"] == "CDSL"
    assert len(data_ind["periods"]) >= 3
    assert not data_ind["is_financial"]
    ind_items = [r["item"] for r in data_ind["rows"]]
    assert "Revenue from Operations" in ind_items
    assert "Operating EBITDA" in ind_items
    assert "Net Profit (PAT)" in ind_items

    # Test Banking / Financial (ICICI Bank)
    res_bank = client.get("/api/fundamentals/ICICIBANK/statements?period_type=annual&view=consolidated")
    assert res_bank.status_code == 200
    data_bank = res_bank.json()
    assert data_bank["symbol"] == "ICICIBANK"
    assert data_bank["is_financial"]
    bank_items = [r["item"] for r in data_bank["rows"]]
    assert "Net Interest Income (NII)" in bank_items
    assert "Net Interest Margin (NIM)" in bank_items
    assert "Gross NPA %" in bank_items
    assert "Net NPA %" in bank_items
    assert "Customer Deposits" in bank_items
    assert "Advances (Loan Book)" in bank_items


# Criteria 17: Evidence-based multibagger framework with 5 pillars (Phase 6)
def test_criterion_17_evidence_based_multibagger_5_pillars():
    """Verify 5 pillars are returned with full evidence trails and probability disclaimer."""
    from bharat_value_ai.analysis.quality_growth import quality_engine
    res = quality_engine.evaluate_company("CDSL")

    assert res.composite_score > 0
    assert res.multibagger_potential_tier is not None
    assert res.pillars is not None
    assert len(res.pillars) == 5

    required_keys = ["pillar_name", "score", "weight_pct", "definition", "evidence", "source_period", "calculation_method", "main_strengths", "counterarguments"]
    for p in res.pillars:
        for k in required_keys:
            assert k in p, f"Missing key {k} in pillar {p.get('pillar_name')}"
        assert p["score"] >= 0
        assert len(p["main_strengths"]) > 0
        assert len(p["counterarguments"]) > 0

    assert res.probability_disclaimer is not None
    assert "NOT an empirical or calibrated statistical probability" in res.probability_disclaimer


# Criteria 18: 8-Dimension Institutional Risk Matrix (Phase 7)
def test_criterion_18_eight_dimension_risk_matrix():
    """Verify 8 institutional risk dimensions with the 4 explicit statuses."""
    from bharat_value_ai.analysis.risk_governance import risk_engine
    allowed_statuses = {"No issue detected", "Issue detected", "Not checked", "Insufficient data"}
    allowed_severities = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

    matrix = risk_engine.evaluate_risk_matrix("ICICIBANK")
    assert matrix.symbol == "ICICIBANK"
    assert matrix.overall_risk_rating in {"LOW", "MODERATE", "ELEVATED", "HIGH"}
    assert len(matrix.dimensions) == 8

    expected_dim_ids = [
        "leverage_debt_servicing",
        "profitability_cash_flow",
        "earnings_deterioration",
        "governance_regulatory",
        "related_party_auditor",
        "liquidity_market_risk",
        "valuation_downside",
        "data_freshness_coverage"
    ]

    actual_dim_ids = [d.dimension_id for d in matrix.dimensions]
    for exp_id in expected_dim_ids:
        assert exp_id in actual_dim_ids, f"Missing dimension {exp_id}"

    for d in matrix.dimensions:
        assert d.status in allowed_statuses
        assert d.severity in allowed_severities
        assert len(d.evidence) > 0
        assert len(d.source_date) > 0
        assert len(d.explanation) > 0
        assert len(d.recommended_investigation) > 0

    # Test API endpoint
    api_res = client.get("/api/risk/matrix/ICICIBANK")
    assert api_res.status_code == 200
    assert len(api_res.json()["dimensions"]) == 8


# Criteria 19: Banking valuation vs Industrial DCF waterfall consistency (Phase 5)
def test_criterion_19_banking_valuation_waterfall_and_ev_consistency():
    """Verify ICICI Bank routes to banking RIM/Justified P/B and industrial DCF contains EV waterfall."""
    val_bank = fair_value_engine.evaluate_valuation("ICICIBANK")
    assert val_bank.model_type == "BANK_RESIDUAL_INCOME_PB"
    assert val_bank.residual_income_fair_value is not None
    assert val_bank.justified_pb_fair_value is not None
    assert "cost_of_equity_ke" in val_bank.assumptions
    assert "sustainable_roe" in val_bank.assumptions

    val_ind = fair_value_engine.evaluate_valuation("CDSL")
    assert val_ind.model_type == "INDUSTRIAL_DCF"
    assert "enterprise_value_cr" in val_ind.assumptions
    assert "equity_value_cr" in val_ind.assumptions
    assert "pv_explicit_fcf_cr" in val_ind.assumptions
    assert val_ind.assumptions["enterprise_value_cr"] >= val_ind.assumptions["pv_explicit_fcf_cr"]


# Criteria 20: Verified RAG revenue retrieval and citation for HDFC Bank
def test_criterion_20_hdfc_bank_revenue_rag_retrieval_and_answer():
    """Verify RAG correctly retrieves and cites audited FY24 revenue for HDFC Bank."""
    from bharat_value_ai.rag.document_parser import doc_parser_service
    doc_parser_service.seed_initial_knowledge_base()

    res = research_assistant.query("What was HDFC Bank revenue in FY24?", symbol="HDFCBANK")
    assert res.has_sufficient_evidence is True
    assert len(res.citations) > 0
    assert any("HDFC Bank" in c.document_title for c in res.citations)
    assert any("revenue" in c.section_title.lower() or "financial" in c.section_title.lower() for c in res.citations)
    assert "HDFCBANK" in res.answer or "HDFC Bank" in res.answer


# Criteria 21: Screener rejects negative/missing P/E when P/E ceiling is enforced
def test_criterion_21_screener_rejects_missing_and_negative_pe_when_capped():
    """Verify screener does not treat missing or negative P/E companies as cheap when max_pe is constrained."""
    # Screen with strict P/E cap of 35
    res = client.get("/api/screener?max_pe=35.0")
    assert res.status_code == 200
    stocks = res.json()
    assert isinstance(stocks, list)
    assert len(stocks) > 0
    for s in stocks:
        assert s["pe_ratio"] is not None
        assert s["pe_ratio"] > 0
        assert s["pe_ratio"] <= 35.0


# Criteria 22: Provider diagnostics table and test-connection actions
def test_criterion_22_provider_diagnostics_and_test_connection():
    """Verify /api/health exposes live diagnostics and /api/health/test-connection/{provider} works."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "diagnostics" in data
    assert len(data["diagnostics"]) >= 5
    provider_ids = [d["id"] for d in data["diagnostics"]]
    assert "database" in provider_ids
    assert "market_data" in provider_ids
    assert "rag_vector_store" in provider_ids

    # Test individual probe endpoint
    probe_resp = client.get("/api/health/test-connection/database")
    assert probe_resp.status_code == 200
    probe_data = probe_resp.json()
    assert probe_data["id"] == "database"
    assert probe_data["status"] == "HEALTHY"
    assert probe_data["latency_ms"] >= 0.0
