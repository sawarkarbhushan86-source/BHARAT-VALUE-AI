"""Unit tests for Financial NLP sentiment, event classification, and deduplication."""
from bharat_value_ai.nlp.sentiment import sentiment_analyzer
from bharat_value_ai.nlp.event_classifier import event_classifier
from bharat_value_ai.nlp.entity_extractor import entity_extractor
from bharat_value_ai.nlp.materiality import materiality_engine
from bharat_value_ai.nlp.deduplication import news_deduplicator

def test_financial_sentiment_positive():
    text = "Company reported robust Q3 performance with profit surge and EBITDA margin expansion."
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment_label"] == "POSITIVE"
    assert res["probabilities"]["positive"] > res["probabilities"]["negative"]
    assert res["confidence"] > 0.5
    assert len(res["explanation"]["positive_drivers"]) > 0

def test_financial_sentiment_negative():
    text = "SEBI penalty and auditor resignation triggered sharp profit slump and probe."
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment_label"] == "NEGATIVE"
    assert res["probabilities"]["negative"] > res["probabilities"]["positive"]
    assert res["confidence"] > 0.5

def test_financial_sentiment_neutral():
    text = "Board of directors meeting scheduled on 24th October to consider financial statements."
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment_label"] in ["NEUTRAL", "MIXED"]

def test_event_classification():
    order_win = event_classifier.classify("Suzlon Energy bags 1,166 MW wind energy order from NTPC")
    assert order_win["event_category"] == "ORDER_WIN"

    reg_action = event_classifier.classify("SEBI issues show cause notice to company promoters")
    assert reg_action["event_category"] == "REGULATORY_ACTION"

    capex = event_classifier.classify("Company announces capex of ₹4,000 Cr for gigafactory plant expansion")
    assert capex["event_category"] == "CAPEX_EXPANSION"

def test_entity_extraction():
    text = "Exide Industries invested ₹4,000 crore while SEBI scrutinized 14.5% equity pledge."
    ents = entity_extractor.extract(text)
    assert any("4,000" in m or "crore" in m for m in ents["monetary_values"])
    assert any("14.5%" in p for p in ents["percentages"])
    assert "SEBI" in ents["regulators"]

def test_materiality_scoring():
    high_mat = materiality_engine.calculate_materiality(
        event_category="REGULATORY_ACTION",
        source_category="official_filing",
        has_monetary_value=True,
        is_original_disclosure=True
    )
    low_mat = materiality_engine.calculate_materiality(
        event_category="GENERAL_MARKET",
        source_category="rss",
        has_monetary_value=False,
        is_original_disclosure=False
    )
    assert high_mat > low_mat
    assert high_mat >= 0.85

def test_news_deduplication_clusters():
    articles = [
        {"title": "Suzlon Energy secures 1166 MW order from NTPC Green", "summary": "Mega wind contract in Gujarat"},
        {"title": "Suzlon bags 1,166 MW wind energy order from NTPC Green Ltd", "summary": "Contract for Gujarat project"},
        {"title": "CDSL active demat accounts cross 115 million mark", "summary": "Depository achieves milestone"}
    ]
    clustered = news_deduplicator.cluster_articles(articles)
    assert len(clustered) == 3
    # First two articles should share same cluster ID
    assert clustered[0]["duplicate_cluster_id"] == clustered[1]["duplicate_cluster_id"]
    # Third article belongs to distinct cluster
    assert clustered[0]["duplicate_cluster_id"] != clustered[2]["duplicate_cluster_id"]
