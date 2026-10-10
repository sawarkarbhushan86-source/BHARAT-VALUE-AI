"""Pydantic V2 Request and Response Schemas."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

# Base configuration for Pydantic V2
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ----------------- Company & Quotes -----------------
class CompanySummary(BaseSchema):
    id: int
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap_category: str = "Smallcap"
    market_cap_cr: Optional[float] = None
    isin: Optional[str] = None
    bse_code: Optional[str] = None

class QuoteResponse(BaseSchema):
    symbol: str
    exchange: str = "NSE"
    price: float
    change: float
    change_percent: float
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    previous_close: Optional[float] = None
    volume: int = 0
    turnover_cr: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    data_source: str = "yfinance"
    is_delayed: bool = True
    quote_timestamp: datetime
    retrieval_timestamp: datetime

class CandleResponse(BaseSchema):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

# ----------------- Financial Fundamentals -----------------
class FinancialStatementResponse(BaseSchema):
    id: int
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    period_type: str = "annual"
    revenue: Optional[float] = None
    operating_profit: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    operating_margin_pct: Optional[float] = None
    net_margin_pct: Optional[float] = None
    roe_pct: Optional[float] = None
    roce_pct: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    promoter_holding_pct: Optional[float] = None
    promoter_pledge_pct: Optional[float] = None
    altman_z_score: Optional[float] = None
    public_availability_date: Optional[datetime] = None

class DuPontAnalysisResponse(BaseSchema):
    symbol: str
    fiscal_year: int
    roe_pct: float
    net_profit_margin_pct: float
    asset_turnover: float
    equity_multiplier: float
    tax_burden_ratio: Optional[float] = None
    interest_burden_ratio: Optional[float] = None
    ebit_margin_pct: Optional[float] = None
    interpretation: str

# ----------------- Fair Value & DCF -----------------
class DCFParameters(BaseModel):
    symbol: str
    forecast_years: int = Field(default=5, ge=3, le=10)
    revenue_growth_rate: float = Field(default=0.15, ge=-0.20, le=0.60)
    operating_margin: float = Field(default=0.18, ge=0.01, le=0.70)
    tax_rate: float = Field(default=0.25, ge=0.0, le=0.40)
    reinvestment_rate: float = Field(default=0.20, ge=0.0, le=0.60)
    discount_rate_wacc: float = Field(default=0.12, ge=0.07, le=0.25)
    terminal_growth_rate: float = Field(default=0.05, ge=0.02, le=0.08)

class ValuationResult(BaseSchema):
    symbol: str
    current_price: float
    dcf_fair_value: float
    pe_fair_value: float
    ev_ebitda_fair_value: float
    composite_fair_value: float
    margin_of_safety_pct: float
    bear_case_value: float
    base_case_value: float
    bull_case_value: float
    valuation_status: str # "UNDERVALUED", "FAIRLY_VALUED", "OVERVALUED"
    assumptions: Dict[str, Any]
    sensitivity_matrix: List[List[float]]
    sensitivity_wacc_labels: List[float]
    sensitivity_growth_labels: List[float]

# ----------------- Business Quality & Growth -----------------
class QualityScoreResponse(BaseSchema):
    symbol: str
    composite_score: float # 0 to 100
    business_quality_score: float # 0 to 100
    financial_strength_score: float # 0 to 100
    growth_potential_score: float # 0 to 100
    valuation_attractiveness_score: float # 0 to 100
    governance_score: float # 0 to 100
    multibagger_potential_tier: str # "High Conviction", "Selective Growth", "Average", "Speculative", "High Risk"
    factor_breakdown: Dict[str, Any]
    limitations: List[str]

# ----------------- News & NLP -----------------
class NewsArticleResponse(BaseSchema):
    id: int
    internal_id: str
    publisher: str
    title: str
    canonical_url: Optional[str] = None
    summary: Optional[str] = None
    published_at: datetime
    retrieved_at: datetime
    sentiment_label: str
    sentiment_score: float
    sentiment_probabilities: Optional[Dict[str, float]] = None
    event_category: str
    materiality_score: float
    entities: Optional[Dict[str, Any]] = None
    matching_symbols: List[str] = []

class EventStudyResponse(BaseSchema):
    event_id: str
    symbol: str
    event_date: datetime
    event_category: str
    title: str
    reaction_1d_pct: Optional[float] = None
    reaction_5d_pct: Optional[float] = None
    reaction_20d_pct: Optional[float] = None
    benchmark_1d_pct: Optional[float] = None
    abnormal_return_1d_pct: Optional[float] = None
    volume_shock_ratio: Optional[float] = None

# ----------------- RAG & Evidence -----------------
class Citation(BaseSchema):
    document_title: str
    reporting_period: Optional[str] = None
    publication_date: Optional[str] = None
    section_title: Optional[str] = None
    snippet: str
    source_url: Optional[str] = None
    relevance_score: float

class RAGQueryRequest(BaseModel):
    query: str
    symbol: Optional[str] = None
    date_cutoff: Optional[str] = None
    top_k: int = 4

class RAGQueryResponse(BaseSchema):
    query: str
    answer: str
    has_sufficient_evidence: bool
    citations: List[Citation]
    contradicting_evidence: Optional[List[str]] = None
    missing_information: Optional[List[str]] = None
    model_used: str

# ----------------- Risk & Governance -----------------
class RiskFlagResponse(BaseSchema):
    id: int
    symbol: str
    flag_code: str
    category: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    supporting_data: Optional[Dict[str, Any]] = None
    evidence_source: Optional[str] = None
    confidence: float
    date_identified: datetime

# ----------------- Backtest & ML -----------------
class BacktestRequest(BaseModel):
    strategy_name: str = "Quality_Value_Momentum"
    start_date: str = "2021-01-01"
    end_date: str = "2024-01-01"
    rebalance_frequency_days: int = 30
    top_n_stocks: int = 15
    include_costs: bool = True
    brokerage_pct: float = 0.0005
    stt_pct: float = 0.001
    slippage_pct: float = 0.0005

class BacktestResponse(BaseSchema):
    strategy_name: str
    start_date: str
    end_date: str
    total_return_pct: float
    cagr_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    benchmark_return_pct: float
    alpha_pct: float
    turnover_annual_pct: float
    cost_drag_pct: float
    equity_curve: List[Dict[str, Any]] # [{"date": ..., "strategy": ..., "benchmark": ...}]
    assumptions_and_limitations: List[str]

class MLRankingResponse(BaseSchema):
    model_version: str
    rank_timestamp: datetime
    horizon_days: int
    top_ranked: List[Dict[str, Any]]
    bottom_ranked: List[Dict[str, Any]]
    spearman_rank_correlation: float
    feature_importance: Dict[str, float]

# ----------------- Multi-Agent Research -----------------
class MultiAgentResearchRequest(BaseModel):
    symbol: str
    detailed: bool = True

class AgentOutput(BaseSchema):
    agent_name: str
    role: str
    status: str
    findings: Dict[str, Any]
    evidence_sources: List[str]
    limitations: List[str]

class MultiAgentResearchResponse(BaseSchema):
    symbol: str
    company_name: str
    timestamp: datetime
    agents: List[AgentOutput]
    synthesis_report: str
    overall_sentiment: str
    fair_value_estimate: float
    key_risks: List[str]
    audit_trail: List[str]

# ----------------- Health & Status -----------------
class HealthStatus(BaseSchema):
    status: str
    app_name: str
    timestamp: datetime
    active_providers: Dict[str, str]
    database: str
    cached_symbols: int
    news_articles_indexed: int
    documents_indexed: int
