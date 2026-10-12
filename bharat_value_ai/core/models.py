"""SQLAlchemy Database Models for Bharat Value AI."""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship

from bharat_value_ai.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(30), unique=True, index=True, nullable=False) # e.g. CDSL, SUZLON
    bse_code = Column(String(20), index=True, nullable=True)             # e.g. 540608
    isin = Column(String(30), index=True, nullable=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), index=True, nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap_category = Column(String(50), default="Smallcap")         # Smallcap, Midcap, Largecap
    market_cap_cr = Column(Float, nullable=True)                         # Market cap in INR Crores
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    quotes = relationship("Quote", back_populates="company", cascade="all, delete-orphan")
    financials = relationship("FinancialStatement", back_populates="company", cascade="all, delete-orphan")
    valuation_runs = relationship("ValuationRun", back_populates="company", cascade="all, delete-orphan")
    news_matches = relationship("NewsCompanyMatch", back_populates="company", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    risk_flags = relationship("RiskFlag", back_populates="company", cascade="all, delete-orphan")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    symbol = Column(String(30), index=True, nullable=False)
    exchange = Column(String(10), default="NSE")
    price = Column(Float, nullable=False)
    change = Column(Float, default=0.0)
    change_percent = Column(Float, default=0.0)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    previous_close = Column(Float, nullable=True)
    volume = Column(Integer, default=0)
    turnover_cr = Column(Float, nullable=True)
    week_52_high = Column(Float, nullable=True)
    week_52_low = Column(Float, nullable=True)
    data_source = Column(String(50), default="yfinance")
    is_delayed = Column(Boolean, default=True)
    quote_timestamp = Column(DateTime, nullable=False)
    retrieval_timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="quotes")


class Candle(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    symbol = Column(String(30), index=True, nullable=False)
    exchange = Column(String(10), default="NSE")
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    frequency = Column(String(10), default="1d") # '1d', '1wk', '1mo'
    is_adjusted = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_candle_symbol_ts", "symbol", "timestamp", unique=True),
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False) # e.g. 2024
    fiscal_quarter = Column(Integer, nullable=True) # 1, 2, 3, 4 or None for FY
    period_type = Column(String(20), default="annual") # 'annual', 'quarterly'
    reporting_date = Column(DateTime, nullable=False)
    public_availability_date = Column(DateTime, nullable=True) # Point-in-time timestamp
    currency = Column(String(10), default="INR")
    is_consolidated = Column(Boolean, default=True)

    # Core Financial Figures (INR Crores)
    revenue = Column(Float, nullable=True)
    operating_profit = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    total_equity = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    cash_and_equivalents = Column(Float, nullable=True)
    operating_cash_flow = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)

    # Key Ratios
    gross_margin_pct = Column(Float, nullable=True)
    operating_margin_pct = Column(Float, nullable=True)
    net_margin_pct = Column(Float, nullable=True)
    roe_pct = Column(Float, nullable=True)
    roce_pct = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev_to_ebitda = Column(Float, nullable=True)
    working_capital_days = Column(Float, nullable=True)
    cash_conversion_cycle = Column(Float, nullable=True)

    # Governance & Shareholding
    promoter_holding_pct = Column(Float, nullable=True)
    promoter_pledge_pct = Column(Float, nullable=True)
    altman_z_score = Column(Float, nullable=True)

    data_source = Column(String(50), default="financial_reports")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="financials")

    __table_args__ = (
        Index("idx_fin_company_period", "company_id", "fiscal_year", "fiscal_quarter", "period_type", unique=True),
    )


class ValuationRun(Base):
    __tablename__ = "valuation_runs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    run_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    current_price = Column(Float, nullable=False)
    
    # Valuation Output
    dcf_fair_value = Column(Float, nullable=True)
    pe_fair_value = Column(Float, nullable=True)
    ev_ebitda_fair_value = Column(Float, nullable=True)
    composite_fair_value = Column(Float, nullable=False)
    margin_of_safety_pct = Column(Float, nullable=False)
    
    # Scenarios
    bear_case_value = Column(Float, nullable=True)
    base_case_value = Column(Float, nullable=True)
    bull_case_value = Column(Float, nullable=True)
    
    # Parameters
    discount_rate = Column(Float, default=0.12)
    terminal_growth_rate = Column(Float, default=0.05)
    assumptions_json = Column(JSON, nullable=True)
    valuation_status = Column(String(50), default="COMPLETED") # COMPLETED, INSUFFICIENT_DATA

    company = relationship("Company", back_populates="valuation_runs")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    internal_id = Column(String(64), unique=True, index=True, nullable=False)
    canonical_url = Column(String(500), nullable=True)
    publisher = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime, index=True, nullable=False)
    retrieved_at = Column(DateTime, default=datetime.datetime.utcnow)
    language = Column(String(10), default="en")
    source_category = Column(String(50), default="financial_media") # official_filing, financial_media, rss
    is_original_disclosure = Column(Boolean, default=False)
    duplicate_cluster_id = Column(String(64), nullable=True, index=True)
    
    # NLP Classifications
    sentiment_label = Column(String(20), default="NEUTRAL") # POSITIVE, NEGATIVE, NEUTRAL, MIXED
    sentiment_score = Column(Float, default=0.0)           # -1.0 to 1.0
    sentiment_probabilities = Column(JSON, nullable=True)   # {"positive": 0.8, "negative": 0.1, ...}
    event_category = Column(String(50), default="GENERAL_MARKET")
    materiality_score = Column(Float, default=0.5)         # 0.0 to 1.0
    entities_json = Column(JSON, nullable=True)
    nlp_model_version = Column(String(50), default="FinBERT-Hybrid-1.0")

    matches = relationship("NewsCompanyMatch", back_populates="article", cascade="all, delete-orphan")


class NewsCompanyMatch(Base):
    __tablename__ = "news_company_matches"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    symbol = Column(String(30), index=True, nullable=False)
    confidence_score = Column(Float, default=1.0) # 0.0 to 1.0
    matching_method = Column(String(50), default="ticker_exact") # ticker_exact, entity_name, alias
    verification_status = Column(String(20), default="VERIFIED") # VERIFIED, REVIEW_NEEDED

    article = relationship("NewsArticle", back_populates="matches")
    company = relationship("Company", back_populates="news_matches")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), default="annual_report") # annual_report, quarterly_presentation, filing
    reporting_period = Column(String(50), nullable=True) # e.g. FY24, Q3FY24
    filing_date = Column(DateTime, nullable=True)
    source_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    ingestion_version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    company_id = Column(Integer, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    section_title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    flag_code = Column(String(50), index=True, nullable=False)
    category = Column(String(50), nullable=False) # CashFlow, Leverage, Governance, Valuation, Auditor
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    supporting_data = Column(JSON, nullable=True)
    evidence_source = Column(String(255), nullable=True)
    confidence = Column(Float, default=0.95)
    date_identified = Column(DateTime, default=datetime.datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

    company = relationship("Company", back_populates="risk_flags")


class MLRankingRecord(Base):
    __tablename__ = "ml_ranking_records"

    id = Column(Integer, primary_key=True, index=True)
    run_timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    model_version = Column(String(50), default="XGBoost-Ranker-v1.0")
    symbol = Column(String(30), index=True, nullable=False)
    horizon_days = Column(Integer, default=60)
    rank_score = Column(Float, nullable=False)
    predicted_excess_return = Column(Float, nullable=True)
    actual_excess_return = Column(Float, nullable=True)
    features_snapshot = Column(JSON, nullable=True)


class BacktestRecord(Base):
    __tablename__ = "backtest_records"

    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_return_pct = Column(Float, nullable=False)
    cagr_pct = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown_pct = Column(Float, nullable=False)
    benchmark_return_pct = Column(Float, nullable=False)
    turnover_annual_pct = Column(Float, nullable=True)
    parameters_json = Column(JSON, nullable=True)
    equity_curve_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ProviderHealthRecord(Base):
    __tablename__ = "provider_health_records"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(100), index=True, nullable=False)
    endpoint = Column(String(255), nullable=True)
    status = Column(String(20), default="HEALTHY") # HEALTHY, DEGRADED, DOWN
    latency_ms = Column(Float, default=0.0)
    last_check = Column(DateTime, default=datetime.datetime.utcnow)
    error_message = Column(Text, nullable=True)


class HistoricalIngestionJob(Base):
    __tablename__ = "historical_ingestion_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(64), unique=True, index=True, nullable=False)
    data_type = Column(String(50), default="candles") # candles, fundamentals, corporate_actions
    symbols_json = Column(JSON, nullable=True)
    status = Column(String(20), default="COMPLETED") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    records_ingested = Column(Integer, default=0)
    failed_symbols_json = Column(JSON, nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    provider = Column(String(50), default="yfinance")
    error_message = Column(Text, nullable=True)

