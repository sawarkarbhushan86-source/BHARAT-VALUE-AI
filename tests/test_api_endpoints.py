"""End-to-End API Integration Tests for Bharat Value AI."""
from fastapi.testclient import TestClient
from bharat_value_ai.main import app

client = TestClient(app)

def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "BHARAT VALUE AI" in response.text
    assert "Plotly" in response.text

def test_api_market_status():
    response = client.get("/api/market/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_open" in data

def test_api_get_quote():
    response = client.get("/api/market/quote/CDSL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "CDSL"
    assert data["price"] > 0

def test_api_screener():
    response = client.get("/api/screener?min_roce=15&max_pe=100")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_api_valuation():
    response = client.get("/api/valuation/CDSL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "CDSL"
    assert data["composite_fair_value"] > 0

def test_api_quality():
    response = client.get("/api/growth/quality/CDSL")
    assert response.status_code == 200
    data = response.json()
    assert data["composite_score"] > 0

def test_api_nlp_analyze():
    response = client.post("/api/nlp/analyze", json={"text": "Suzlon bags 1166 MW wind energy contract from NTPC"})
    assert response.status_code == 200
    data = response.json()
    assert data["event_classification"]["event_category"] == "ORDER_WIN"
    assert data["sentiment"]["sentiment_label"] == "POSITIVE"

def test_api_rag_query():
    from bharat_value_ai.rag.document_parser import doc_parser_service
    doc_parser_service.seed_initial_knowledge_base()

    response = client.post("/api/rag/query", json={
        "query": "What did CDSL report regarding active Demat accounts in FY24?",
        "symbol": "CDSL"
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["citations"]) > 0

def test_api_agents_research():
    response = client.get("/api/agents/research/CDSL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "CDSL"
    assert len(data["agents"]) == 6

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
