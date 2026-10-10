"""FastAPI Endpoints for Bharat Value AI Platform."""
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse

from bharat_value_ai.core.schemas import (
    QuoteResponse, CandleResponse, FinancialStatementResponse,
    DuPontAnalysisResponse, DCFParameters, ValuationResult,
    QualityScoreResponse, NewsArticleResponse, EventStudyResponse,
    RAGQueryRequest, RAGQueryResponse, RiskFlagResponse,
    BacktestRequest, BacktestResponse, MLRankingResponse,
    MultiAgentResearchResponse, HealthStatus
)
from bharat_value_ai.core.security import sanitize_symbol, is_safe_file_upload
from bharat_value_ai.data.universe import get_complete_universe, find_company_by_symbol
from bharat_value_ai.data.market_provider import market_provider, is_indian_market_open
from bharat_value_ai.data.news_provider import news_service
from bharat_value_ai.nlp.sentiment import sentiment_analyzer
from bharat_value_ai.nlp.event_classifier import event_classifier
from bharat_value_ai.nlp.entity_extractor import entity_extractor
from bharat_value_ai.nlp.materiality import materiality_engine
from bharat_value_ai.nlp.deduplication import news_deduplicator
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.analysis.fair_value import fair_value_engine
from bharat_value_ai.analysis.quality_growth import quality_engine
from bharat_value_ai.analysis.risk_governance import risk_engine
from bharat_value_ai.rag.assistant import research_assistant
from bharat_value_ai.rag.vector_store import vector_store
from bharat_value_ai.rag.document_parser import doc_parser_service
from bharat_value_ai.agents.orchestrator import agent_orchestrator
from bharat_value_ai.ml.pipeline import ml_ranking_lab
from bharat_value_ai.ml.backtester import backtester
from bharat_value_ai.ml.event_study import event_study_engine
from bharat_value_ai.reports.generator import report_generator
from bharat_value_ai.config import settings

api_router = APIRouter(prefix="/api")

# ----------------- 1. Market Data Endpoints -----------------
@api_router.get("/market/status")
def get_market_status():
    """Returns whether the Indian National Stock Exchange (NSE) is currently open."""
    return is_indian_market_open()

@api_router.get("/market/indices")
def get_market_indices():
    """Fetch benchmark indices: Nifty 50, Nifty Smallcap 100, Nifty Bank, India VIX."""
    return market_provider.get_market_indices()

@api_router.get("/market/quote/{symbol}", response_model=QuoteResponse)
def get_quote(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    quote = market_provider.get_quote(clean_sym)
    return QuoteResponse(**quote)

@api_router.get("/market/candles/{symbol}", response_model=List[CandleResponse])
def get_candles(symbol: str, period: str = "3mo"):
    clean_sym = sanitize_symbol(symbol)
    candles = market_provider.get_historical_ohlcv(clean_sym, period=period)
    return [CandleResponse(**c) for c in candles]

@api_router.get("/universe")
def get_universe(search: Optional[str] = None):
    """List supported Indian stock universe with optional search filter."""
    univ = get_complete_universe()
    if search:
        q = search.lower().strip()
        univ = [
            c for c in univ
            if q in c["symbol"].lower() or q in c["name"].lower() or q in c.get("sector", "").lower()
        ]
    return univ

# ----------------- 2. Screener Endpoint -----------------
@api_router.get("/screener")
def run_screener(
    min_roce: float = Query(default=0.0),
    min_roe: float = Query(default=0.0),
    max_pe: float = Query(default=150.0),
    max_debt_to_equity: float = Query(default=3.0),
    min_quality_score: float = Query(default=0.0),
    sector: Optional[str] = None
):
    """Multi-factor stock screener across Nifty Smallcap 100 universe."""
    universe = get_complete_universe()
    screened = []

    for comp in universe:
        sym = comp["symbol"]
        if sector and comp.get("sector") != sector:
            continue

        fund = fundamentals_engine.get_company_fundamentals(sym)
        quote = market_provider.get_quote(sym)
        qual = quality_engine.evaluate_company(sym)
        val = fair_value_engine.evaluate_valuation(sym)

        roce = fund.get("roce_pct", 0.0)
        roe = fund.get("roe_pct", 0.0)
        pe = fund.get("pe_ratio", 0.0)
        dte = fund.get("debt_to_equity", 0.0)
        score = qual.composite_score

        if (roce >= min_roce and roe >= min_roe and pe <= max_pe and
            dte <= max_debt_to_equity and score >= min_quality_score):
            screened.append({
                "symbol": sym,
                "name": comp["name"],
                "sector": comp.get("sector"),
                "price": quote.get("price", 0.0),
                "change_percent": quote.get("change_percent", 0.0),
                "pe_ratio": pe,
                "roce_pct": roce,
                "roe_pct": roe,
                "debt_to_equity": dte,
                "revenue_growth_3y": fund.get("revenue_growth_3y_cagr", 0.0),
                "quality_score": score,
                "fair_value": val.composite_fair_value,
                "margin_of_safety_pct": val.margin_of_safety_pct,
                "valuation_status": val.valuation_status
            })

    return screened

# ----------------- 3. Fundamentals & DuPont -----------------
@api_router.get("/fundamentals/{symbol}")
def get_fundamentals(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    return fundamentals_engine.get_company_fundamentals(clean_sym)

@api_router.get("/fundamentals/dupont/{symbol}", response_model=DuPontAnalysisResponse)
def get_dupont_analysis(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    fund = fundamentals_engine.get_company_fundamentals(clean_sym)
    res = fundamentals_engine.compute_dupont_3_stage(fund)
    res["fiscal_year"] = 2024
    return DuPontAnalysisResponse(**res)

# ----------------- 4. Fair Value & DCF -----------------
@api_router.get("/valuation/{symbol}", response_model=ValuationResult)
def get_valuation(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    return fair_value_engine.evaluate_valuation(clean_sym)

@api_router.post("/valuation/custom", response_model=ValuationResult)
def calculate_custom_valuation(params: DCFParameters):
    clean_sym = sanitize_symbol(params.symbol)
    return fair_value_engine.evaluate_valuation(clean_sym, custom_params=params)

# ----------------- 5. Business Quality -----------------
@api_router.get("/growth/quality/{symbol}", response_model=QualityScoreResponse)
def get_quality_score(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    return quality_engine.evaluate_company(clean_sym)

# ----------------- 6. Financial News & NLP -----------------
@api_router.get("/news/latest")
def get_latest_news(limit: int = 20):
    raw_news = news_service.fetch_latest_news(max_items_per_feed=limit)
    clustered = news_deduplicator.cluster_articles(raw_news)
    
    enriched = []
    for art in clustered[:limit]:
        title = art["title"]
        s_res = sentiment_analyzer.analyze(title)
        e_res = event_classifier.classify(title)
        ents = entity_extractor.extract(title + " " + art.get("summary", ""))
        mat = materiality_engine.calculate_materiality(
            event_category=e_res["event_category"],
            source_category=art.get("source_category", "financial_media"),
            has_monetary_value=bool(ents["monetary_values"]),
            is_original_disclosure=art.get("is_original_story", True)
        )

        matched_syms = [m["symbol"] for m in art.get("matched_companies", [])]

        enriched.append({
            "id": hash(art["internal_id"]) % 1000000,
            "internal_id": art["internal_id"],
            "publisher": art["publisher"],
            "title": title,
            "canonical_url": art.get("canonical_url"),
            "summary": art.get("summary"),
            "published_at": art["published_at"],
            "retrieved_at": art["retrieved_at"],
            "sentiment_label": s_res["sentiment_label"],
            "sentiment_score": s_res["sentiment_score"],
            "sentiment_probabilities": s_res["probabilities"],
            "event_category": e_res["event_category"],
            "materiality_score": mat,
            "entities": ents,
            "matching_symbols": matched_syms,
            "is_original_story": art.get("is_original_story", True),
            "duplicate_cluster_id": art.get("duplicate_cluster_id")
        })

    return enriched

@api_router.get("/news/events", response_model=List[EventStudyResponse])
def get_event_studies(symbol: Optional[str] = None):
    clean_sym = sanitize_symbol(symbol) if symbol else None
    return event_study_engine.get_event_studies(clean_sym)

@api_router.post("/nlp/analyze")
def analyze_custom_headline(payload: Dict[str, str]):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
    
    sentiment = sentiment_analyzer.analyze(text)
    event = event_classifier.classify(text)
    entities = entity_extractor.extract(text)
    materiality = materiality_engine.calculate_materiality(
        event_category=event["event_category"],
        source_category="financial_media",
        has_monetary_value=bool(entities["monetary_values"]),
        is_original_disclosure=True
    )

    return {
        "text": text,
        "sentiment": sentiment,
        "event_classification": event,
        "entities": entities,
        "materiality_score": materiality
    }

# ----------------- 7. RAG Assistant & Documents -----------------
@api_router.post("/rag/query", response_model=RAGQueryResponse)
def query_rag_assistant(req: RAGQueryRequest):
    clean_sym = sanitize_symbol(req.symbol) if req.symbol else None
    return research_assistant.answer_query(
        query=req.query,
        symbol=clean_sym,
        date_cutoff=req.date_cutoff,
        top_k=req.top_k
    )

@api_router.get("/rag/stats")
def get_rag_stats():
    return {
        "indexed_chunks_count": vector_store.count_indexed_chunks(),
        "vector_store_backend": "SQLite Embedded Vector Store",
        "dimension": settings.embedding_dimension
    }

@api_router.post("/rag/upload")
async def upload_document(
    symbol: str,
    title: str,
    period: str,
    file: UploadFile = File(...)
):
    clean_sym = sanitize_symbol(symbol)
    contents = await file.read()
    
    if not is_safe_file_upload(file.filename, len(contents)):
        raise HTTPException(status_code=400, detail="Invalid file type or file size exceeds 25MB limit.")

    text_content = contents.decode("utf-8", errors="ignore")
    chunks = doc_parser_service.chunk_text(text_content)
    
    for idx, c in enumerate(chunks):
        c_id = f"upl_{clean_sym}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx+1}"
        vector_store.add_document_chunk(
            chunk_id=c_id,
            symbol=clean_sym,
            document_title=title,
            reporting_period=period,
            publication_date=datetime.now().strftime("%Y-%m-%d"),
            section_title=f"User Upload Chunk {idx+1}",
            content=c,
            source_url=""
        )

    return {
        "status": "SUCCESS",
        "symbol": clean_sym,
        "filename": file.filename,
        "chunks_indexed": len(chunks)
    }

# ----------------- 8. Multi-Agent Research -----------------
@api_router.get("/agents/research/{symbol}", response_model=MultiAgentResearchResponse)
def run_multi_agent_research(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    return agent_orchestrator.run_research(clean_sym)

# ----------------- 9. ML Ranking & Backtesting -----------------
@api_router.get("/ml/rank", response_model=MLRankingResponse)
def get_ml_ranking(horizon_days: int = 60):
    return ml_ranking_lab.train_and_rank(horizon_days=horizon_days)

@api_router.post("/ml/backtest", response_model=BacktestResponse)
def run_backtest(req: BacktestRequest):
    return backtester.run_backtest(req)

# ----------------- 10. Risk & Governance -----------------
@api_router.get("/risk/flags/{symbol}", response_model=List[RiskFlagResponse])
def get_risk_flags(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    return risk_engine.evaluate_risks(clean_sym)

# ----------------- 11. Reports Generation -----------------
@api_router.get("/reports/pdf/{symbol}")
def download_pdf_report(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    try:
        path = report_generator.generate_pdf_report(clean_sym)
        return FileResponse(
            path=path,
            filename=Path(path).name,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@api_router.get("/reports/csv/{symbol}")
def download_csv_report(symbol: str):
    clean_sym = sanitize_symbol(symbol)
    try:
        path = report_generator.generate_csv_report(clean_sym)
        return FileResponse(
            path=path,
            filename=Path(path).name,
            media_type="text/csv"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate CSV data: {str(e)}")

# ----------------- 12. Health & Settings -----------------
@api_router.get("/health", response_model=HealthStatus)
def get_platform_health():
    now_utc = datetime.now(timezone.utc)
    return HealthStatus(
        status="HEALTHY",
        app_name=settings.app_name,
        timestamp=now_utc,
        active_providers={
            "market_data": "Yahoo Finance (NSE Delayed 15m) & Cached Baseline",
            "news_feeds": "Moneycontrol, Economic Times, Livemint RSS",
            "rag_vector_store": "SQLite Embedded Vector Store",
            "llm_engine": "Google Gemini 2.5 Flash / Deterministic Evidence Synthesizer"
        },
        database="SQLite Local / PostgreSQL Ready",
        cached_symbols=len(get_complete_universe()),
        news_articles_indexed=18,
        documents_indexed=vector_store.count_indexed_chunks()
    )

@api_router.get("/settings")
def get_settings():
    return {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "default_exchange": settings.default_exchange,
        "gemini_api_configured": bool(settings.gemini_api_key),
        "news_api_configured": bool(settings.news_api_key),
        "promoter_pledge_threshold": settings.promoter_pledge_high_threshold,
        "debt_to_equity_threshold": settings.debt_to_equity_max_threshold,
        "brokerage_pct": settings.default_brokerage_pct,
        "stt_pct": settings.default_stt_pct,
        "slippage_pct": settings.default_slippage_pct
    }

@api_router.post("/settings")
def update_settings(payload: Dict[str, Any]):
    if "gemini_api_key" in payload:
        settings.gemini_api_key = payload["gemini_api_key"]
    if "default_exchange" in payload:
        settings.default_exchange = payload["default_exchange"]
    return {"status": "SUCCESS", "message": "Settings updated."}
