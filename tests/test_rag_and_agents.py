"""Unit tests for Evidence-Grounded RAG and Controlled Multi-Agent Orchestration."""
from bharat_value_ai.rag.vector_store import vector_store
from bharat_value_ai.rag.document_parser import doc_parser_service
from bharat_value_ai.rag.assistant import research_assistant
from bharat_value_ai.agents.orchestrator import agent_orchestrator

def test_vector_store_indexing_and_search():
    doc_parser_service.seed_initial_knowledge_base()
    assert vector_store.count_indexed_chunks() > 0

    # Search for CDSL demat milestone
    results = vector_store.search(query="demat accounts milestone active", symbol="CDSL", top_k=2)
    assert len(results) > 0
    assert results[0]["symbol"] == "CDSL"
    assert "115 million" in results[0]["content"]

def test_rag_assistant_with_evidence():
    response = research_assistant.answer_query(
        query="What did CDSL report regarding its Demat accounts and operating margin?",
        symbol="CDSL"
    )
    assert response.has_sufficient_evidence is True
    assert len(response.citations) > 0
    assert any("CDSL" in c.document_title for c in response.citations)
    assert "CDSL" in response.answer

def test_rag_assistant_insufficient_evidence():
    # An obscure question with no indexed document evidence
    response = research_assistant.answer_query(
        query="What was the gold mining extraction quota in Antarctica during 1920?",
        symbol="CDSL"
    )
    # Must flag insufficient evidence and avoid fabricating answers
    assert response.has_sufficient_evidence is False
    assert "Insufficient verifiable evidence" in response.answer
    assert len(response.citations) == 0

def test_rag_assistant_cross_company_mention_priority():
    """Verify that an explicit company mention in query overrides default symbol parameter."""
    doc_parser_service.seed_initial_knowledge_base()
    # Query mentions Suzlon and NTPC, but ambient symbol passed is CDSL
    response = research_assistant.answer_query(
        query="What order did Suzlon get from NTPC?",
        symbol="CDSL"
    )
    assert response.has_sufficient_evidence is True
    assert any("Suzlon" in c.document_title for c in response.citations)
    assert "Suzlon" in response.answer

def test_multi_agent_orchestration():
    res = agent_orchestrator.run_research("CDSL")
    assert res.symbol == "CDSL"
    assert len(res.agents) == 6 # Fundamental, Valuation, News, Quality, Risk, Skeptical Reviewer
    assert res.fair_value_estimate > 0
    assert len(res.audit_trail) > 0
    assert any("Skeptical Reviewer" in a.agent_name for a in res.agents)
    assert any("Fundamental Analyst" in a.agent_name for a in res.agents)
