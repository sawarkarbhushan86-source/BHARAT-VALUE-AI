# BHARAT VALUE AI
## AI-Powered Indian Stock Market Intelligence, Valuation, Financial News NLP, RAG & Multibagger Research Platform

BHARAT VALUE AI is an institutional-grade investment research and decision-support platform engineered specifically for Indian equities listed on the **National Stock Exchange (NSE)** and **Bombay Stock Exchange (BSE)**.

Focusing initially on the **Nifty Smallcap 100** universe (with built-in architecture to expand to Nifty 500 and broader listed equities), the platform enables analysts and investors to investigate business fundamentals, compute deterministic fair values, track live news and market events, uncover governance red flags, conduct evidence-grounded RAG research, and run point-in-time quantitative backtests.

---

## 🌟 Core Architecture & Platform Modules

1. **Market Overview Dashboard**: Real-time / delayed feeds for Nifty 50, Nifty Smallcap 100, Nifty Bank, and India VIX with live NSE trading calendar session detection (open, closed, weekend, exchange holidays).
2. **Quantitative Stock Screener**: Multi-factor screener filtering companies across ROCE, ROE, P/E, Debt-to-Equity, 3Y Growth, and Quality Score.
3. **Stock Details & Interactive Charts**: Live market quotes, volume turnover, 52-week range, and high-frequency Plotly.js candlestick OHLCV charts with volume bars.
4. **Fundamental Analysis & DuPont Decomposition**: 5-Year audited figures, DuPont 3-stage ROE driver breakdown (Net Margin × Asset Turnover × Financial Leverage), and working-capital cash conversion cycle.
5. **Deterministic Fair-Value Calculator**: Mathematically verified DCF model with interactive growth/WACC sliders, 2D sensitivity matrix heatmap, sector relative multiples (P/E & EV/EBITDA), Bear/Base/Bull scenarios, and Margin of Safety.
6. **Business Quality & Multibagger Framework**: 5-pillar compounding analysis (Moat, Financial Strength, Growth Runway, Valuation, Governance) over 5–10 year holding horizons.
7. **Financial News Aggregation**: Automated RSS feeds from Moneycontrol, Economic Times, Livemint, and official corporate announcements with company-level matching and publisher attribution.
8. **Company News Timeline & Event Studies**: Chronological corporate disclosures mapped against 1D, 5D, and 20D abnormal returns and volume shocks.
9. **Financial NLP & FinBERT Event Lab**: Calibrated sentiment probabilities (Positive, Negative, Neutral, Mixed), 16 standardized financial event categories (Earnings Beat, Order Win, Capex, SEBI Action, etc.), entity extraction, and materiality scoring.
10. **Evidence-Grounded RAG Research Assistant**: RAG assistant with semantic vector retrieval over audited annual reports and filings. Every answer cites exact documents and reporting periods with clickable evidence citations. Enforces a strict insufficient-evidence guardrail to prevent hallucinations.
11. **Controlled Multi-Agent Research Orchestrator**: Deterministic workflow coordinating 6 specialized agents: Fundamental Analyst, Valuation Analyst, News & Event Analyst, Growth Analyst, Risk Analyst, and an Adversarial Skeptical Reviewer with full audit logging.
12. **Quantitative ML Research Lab**: Cross-sectional forward excess return ranking using XGBoost trained on strict chronological time-based splits (preventing look-ahead bias), accompanied by Spearman rank correlation and feature importance metrics.
13. **Walk-Forward Strategy Backtesting**: Strategy simulation factoring in Securities Transaction Tax (STT: 0.1%), brokerage (0.05%), and slippage (0.05%), outputting CAGR, Sharpe Ratio, Sortino Ratio, and Maximum Drawdown equity curves.
14. **Risk & Governance Intelligence**: Forensic red-flag detection covering promoter share pledging (>25%), low interest coverage (<2.5x), cash-flow divergence, and Altman Z-Score distress zones.
15. **Company Research Reports**: Single-click downloadable institutional PDF research reports generated via ReportLab with tables, scenarios, and disclaimers, alongside CSV data export.
16. **API & Data Health Monitoring**: Live status, latency, and cache hit metrics across all providers.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic V2, SQLAlchemy, SQLite (production ready for PostgreSQL)
- **Financial Processing**: Pandas, NumPy, SciPy
- **Market Data**: Yahoo Finance (`yfinance` for `.NS` and `.BO`), Feedparser for RSS news feeds
- **Machine Learning**: XGBoost, Scikit-Learn
- **NLP & RAG**: FinBERT-calibrated Lexical and Probability Engine, Embedded SQLite Vector Store with Cosine Similarity, Google GenAI SDK (`google-genai` / Gemini 2.5 Flash)
- **Report Generation**: ReportLab (institutional PDF formatting), CSV
- **Frontend**: Vanilla ES6+, CSS3 Design Tokens (Glassmorphic Dark Theme), Plotly.js CDN
- **Testing**: Pytest, Pytest-Asyncio, HTTPX

---

## 🚀 Quickstart Guide (Windows)

### 1. Prerequisites
- Python 3.11 or Python 3.12 installed on your system.

### 2. Setup Virtual Environment & Install Dependencies
Open PowerShell in the project directory:
```powershell
# Create virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY` in `.env` if you wish to use Google Gemini for enhanced conversational synthesis. The application runs autonomously with its deterministic evidence synthesis engine if no key is provided.)*

### 4. Run the Automated Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```
*All 37 test cases across API, valuation, NLP, RAG, backtesting, and reports will execute and pass.*

### 5. Launch the Platform
```powershell
.\.venv\Scripts\python.exe -m uvicorn bharat_value_ai.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to:
👉 **http://127.0.0.1:8000**

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```
Navigate to `http://localhost:8000`.

---

## 🧪 Verified Test Suite Summary

- **API Integration Tests**: `tests/test_api_endpoints.py` (10 passing)
- **Financial Calculations & DCF**: `tests/test_financial_calculations.py` (5 passing)
- **Market Data & Provenance**: `tests/test_market_and_provenance.py` (6 passing)
- **NLP Sentiment & Event Studies**: `tests/test_nlp_and_news.py` (7 passing)
- **RAG & Multi-Agent Orchestrator**: `tests/test_rag_and_agents.py` (4 passing)
- **ML Ranking & Backtesting**: `tests/test_ml_and_backtest.py` (3 passing)
- **Report Generator (PDF & CSV)**: `tests/test_reports.py` (2 passing)

**Total: 37 Passed, 0 Failed (100% Pass Rate)**

---

## ⚖️ Regulatory Disclaimer

BHARAT VALUE AI is an investment research, valuation modeling, and decision-support software application. It does not provide personalized investment advice, guaranteed returns, or SEBI-registered buy/sell recommendations. Historical simulations and quantitative models do not guarantee future performance.
