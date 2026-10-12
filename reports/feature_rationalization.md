# BHARAT VALUE AI — Feature Rationalization & Dependency Audit
**Audit Date:** October 11, 2026  
**Auditor:** Principal Fintech Architect & Quantitative Equity Researcher  
**Document Target:** `reports/feature_rationalization.md`  

---

## 1. Executive Summary

This audit evaluates every existing module, page, API route, and background service in BHARAT VALUE AI to eliminate navigation redundancy, consolidate fragmented screens, and protect core institutional workflows.

**Guiding Rule:**  
Do **NOT** destructively delete working backend code, database models, or unit tests. Advanced tools (RAG, Multi-Agent research, ML stock ranking, Strategy backtesting) represent valuable intellectual property with passing unit tests. Instead, rationalize the user journey by consolidating scattered views into a cohesive primary research hub and nesting technical capabilities inside an **Advanced Research Lab**.

---

## 2. Feature Decision Table

| Feature / View | Current Location | Decision | Justification & Architecture Action | Upstream / Downstream Dependencies |
|---|---|---|---|---|
| **Market Overview** | `view-market` (`/api/market/*`) | **Retain & Improve** | Core entrypoint. Displays indices, breadth, session status, and market movers. | Downstream: Topbar, Screener. |
| **Stock Screener** | `view-screener` (`/api/screener`) | **Retain & Improve** | Fundamental discovery tool. Add explicit column units, sorting, and direct "Research" deep-link. | Upstream: `SnapshotService`, `fundamentals_engine`. |
| **Stock Details** | `view-details` (`/api/market/quote/*`) | **Consolidate** | Merge with Fundamentals, Valuation, Growth, and Risk into the **Unified Company Research Hub**. | Upstream: Market providers. Downstream: Research summary. |
| **Fundamental Analysis** | `view-fundamentals` (`/api/fundamentals/*`) | **Consolidate** | Merge into Company Research as the "Financial Statements & DuPont" tab. Retain API endpoints. | Tested by `test_financial_calculations.py`. |
| **Fair-Value Calculator** | `view-valuation` (`/api/valuation/*`) | **Consolidate & Hardened** | Merge into Company Research as the "Valuation & Scenarios" tab. Remove synthetic defaults for uncatalogued stocks. | Tested by `test_institutional_reliability.py`. |
| **Quality & Multibagger** | `view-growth` (`/api/growth/quality/*`) | **Consolidate & Hardened** | Merge into Company Research as the "Quality Scorecard" tab. Eliminate phantom margins for missing data. | Upstream: `fundamentals_engine`. |
| **Risk & Governance** | `view-risk` (`/api/risk/flags/*`) | **Consolidate** | Merge into Company Research as the "Governance & Risk Audit" tab. | Verified null-safe for banks (`HDFCBANK`). |
| **Financial News Feed** | `view-news` (`/api/news/latest`) | **Retain & Upgrade** | Connect directly to NewsAPI via `NEWS_API_KEY` alongside active RSS feeds and exchange filings. | Connected to `sentiment_analyzer`, `event_classifier`. |
| **News-to-Price Events** | `view-timeline` (`/api/news/events`) | **Consolidate** | Place as a sub-view inside News & Events. Validates price reactions to corporate announcements. | Tested by `test_ml_and_backtest.py`. |
| **NLP & FinBERT Lab** | `view-nlp` (`/api/nlp/analyze`) | **Move to Secondary** | An interactive developer/research tool for analyzing arbitrary text. Move under Advanced Lab or News tools. | Tested by `test_nlp_and_news.py`. |
| **RAG Research Assistant** | `view-rag` (`/api/rag/query`) | **Move to Advanced Lab** | Grounded Q&A against official annual reports and exchange filings. Preserves evidence-based research. | Tested by `test_rag_and_agents.py`. |
| **Multi-Agent Workflow** | `view-agents` (`/api/agents/research/*`)| **Move to Advanced Lab** | 6-Agent institutional consensus synthesis. Highly valuable advanced capability. | Uses `SnapshotService` price snapshot. |
| **ML Stock Ranking** | `view-ml` (`/api/ml/rank`) | **Move to Advanced Lab** | Cross-sectional ridge regression ranking. Uncertainty intervals (`±σ`) implemented. | Tested by `test_ml_and_backtest.py`. |
| **Strategy Backtesting** | `view-backtest` (`/api/backtest/run`) | **Move to Advanced Lab** | Walk-forward simulation with STT, slippage, and brokerage drag. Plotly equity curve repaired. | Tested by `test_ml_and_backtest.py`. |
| **Portfolio & Watchlist** | *None* | **Introduce Lightweight** | Implement client-side `localStorage` pinned stocks list with real-time quotes, solving the missing tracking feature without schema churn. | None. |
| **Research Reports** | `view-reports` (`/api/reports/*`) | **Retain & Improve** | Institutional PDF & CSV download center. Tested null-safe for banking and industrial stocks. | Tested by `test_reports.py`. |
| **Platform Settings & Health**| `view-settings`, `view-health` | **Consolidate** | Unify into a single "Settings & System Diagnostics" view showing provider connection health. | Backed by `/api/health`. |

---

## 3. Dependency Trace & Non-Destructive Refactoring Protocol

### 3.1 Backend Routes and Schema Integrity
- **No Route Deletion:** All existing FastAPI routes (`/api/market/*`, `/api/fundamentals/*`, `/api/valuation/*`, `/api/growth/*`, `/api/risk/*`, `/api/rag/*`, `/api/agents/*`, `/api/ml/*`, `/api/backtest/*`) remain 100% active and backward-compatible.
- **No Schema Deletions:** SQLAlchemy tables (`companies`, `quotes`, `financial_statements`, `valuation_runs`, `news_articles`, `documents`, `backtest_runs`) remain intact.
- **Test Integrity:** Every one of the 57 automated tests continues to pass because backend API contracts are strictly preserved.

### 3.2 Frontend Consolidation Architecture
The consolidation is achieved gracefully in the presentation layer:
1. **Primary Navigation (7 Sections):**
   - 1. Overview (`view-market`)
   - 2. Stock Screener (`view-screener`)
   - 3. Company Research (`view-company-hub`: unified view containing Details, 10-Point Summary, Valuation, Fundamentals, Quality, Risk, and Reports for the active stock)
   - 4. Financial Analysis (`view-fundamentals`: standalone multi-company ratio and DuPont explorer)
   - 5. News & Events (`view-news`: NewsAPI stream, company event reactions, and NLP)
   - 6. Watchlist (`view-watchlist`: pinned stocks with live quotes)
   - 7. Research Reports (`view-reports`: export center)
2. **Advanced Research Lab (Collapsible Section):**
   - RAG Assistant (`view-rag`)
   - Multi-Agent Workflow (`view-agents`)
   - ML Stock Ranking (`view-ml`)
   - Strategy Backtesting (`view-backtest`)
3. **Platform Settings & Diagnostics:**
   - Unified Settings & Health (`view-settings`)

---

## 4. Rollback & Preservation Plan

1. **Git Tracking:** All modifications are tracked via Git.
2. **Test Guardrails:** Running `.\.venv\Scripts\python.exe -m pytest` before and after each phase ensures 100% test pass rate with zero regression.
3. **Approval Gate:** No database migrations or destructive removals will be executed without explicit user consent.
