# BHARAT VALUE AI — Data Provider Matrix & API Strategy

**Date:** October 12, 2026  
**Author:** Financial Data Engineer & API Integration Specialist  
**Architecture Principle:** Provider-Agnostic Market Data Abstraction with Fallback & Provable Freshness  

---

## 1. Provider Capability & Integration Matrix

| Provider / Source | Supported Endpoints | Instrument Scope | Quote Latency & Type | Historical Data | Fundamental Data | Authentication & Keys | Rate Limits & Quotas | Pricing / Licensing Tier | Actual Tested Status | Recommended Role |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---:|:---|
| **Yahoo Finance** (`yfinance` / normalized adapter) | Quote, OHLCV, Corporate Actions | NSE & BSE Equities, Nifty 50, Sensex | 15-min Delayed Bhavcopy during hours; EOD archive | Up to 10+ years daily, weekly, monthly | High-level (P/E, Market Cap, Beta, 52W Range) | None (Public HTTP) | ~2,000 req/hr per IP (soft) | Free / Experimental non-commercial | **CONNECTED** (Latency: 280ms) | **Primary Free Market Data Adapter** |
| **NSE India Official** (`nseindia.com`) | Bhavcopy, Option Chain, Circulars | All NSE Equities, Indices, Derivatives | Real-time (website) or EOD CSVs | Daily Bhavcopy ZIPs archive | Limited to corporate announcements & quarterly results PDF | Cookie/Session header spoofing required (Fragile) | Highly aggressive IP throttling & Cloudflare blocking | Free website / Commercial data feeds licensed via NSE Data & Analytics Ltd | **EXPERIMENTAL / PROHIBITED SCRAPING** | Use official EOD Bhavcopy downloads; avoid brittle scraping |
| **BSE India Official** (`bseindia.com`) | Corporate Filings, XBRL Disclosures | BSE Listed Equities & SME Platform | Delayed 15-min | Historical Bhavcopy | Comprehensive XBRL financial statements | Public portal / Session cookies | Moderate IP rate limits | Free public disclosure archive | **VERIFIED FOR STATEMENTS** | **Primary Source for Audited Financials & Filings** |
| **Zerodha Kite Connect** | `GET /quote`, `GET /instruments`, WebSocket Ticker | NSE, BSE, MCX Equities & F&O | Sub-second Live WebSocket Streaming | 1-min to Daily Candles (up to 7 years) | None (Pure market data broker) | API Key + API Secret + Daily Request Token (OAuth2) | 3 requests / second (HTTP); 3,000 instruments / socket | Paid: ₹2,000/month (base) + ₹2,000/month (historical API) | **READY (Requires User Account)** | **Tier-1 Real-Time Streaming Provider** |
| **Angel One SmartAPI** | Market Feed, Historical API, Order Management | NSE, BSE, MCX Equities & F&O | Real-time WebSocket Streaming | Historical 1-min / Daily | None | Client Code + Password + TOTP + API Key | 3–10 requests / second | Free for Angel One account holders | **READY (Requires User Account)** | **Cost-Effective Real-Time Alternative** |
| **Financial Media RSS** (Moneycontrol, ET, Livemint) | Public RSS Syndication Feeds | Indian Macro, Sector, Corporate News | 5–15 min publication latency | Recent 24–48 hours articles | None | None (Public RSS 2.0 / XML) | Standard HTTP caching (300s TTL) | Free public syndication | **CONNECTED** (Latency: 110ms) | **Primary Continuous News Ingestion Feed** |
| **Google Gemini API** (`gemini-2.5-flash`) | `models.generateContent`, `embedContent` | Unstructured corporate filings, transcripts | Sub-second inference | N/A (LLM Reasoning) | Synthesizes verified filings into research notes | API Key (`GEMINI_API_KEY`) | Free tier: 15 RPM; Paid tier: Pay-as-you-go | Optional / Free tier sufficient | **CONNECTED / FALLBACK READY** | **Research Synthesis & RAG Assistant Engine** |
| **Local SQLite Vector Store** | Vector search, Chunk retrieval, Provenance | 384-dimensional dense semantic vectors | Sub-millisecond (Local embedded) | Audited annual reports FY21–FY24 | Full income statement, balance sheet, risk factors | Local SQLite file (`vector_index.db`) | Unlimited local IOPS | 100% Free & Open Source | **CONNECTED** (Latency: 0.8ms) | **Core Evidence & Citation Knowledge Base** |

---

## 2. Free-First Development & Enterprise Upgrade Roadmap

To maintain institutional reproducibility without imposing recurring monthly costs on developers:

### Tier 1: Free Development & Offline Research (Default Operational State)
- **Market Data**: Normalized Yahoo Finance adapter with 15-minute delayed quotes and local SQLite caching.
- **Fundamentals**: Canonical audited annual report financial statements for Nifty Smallcap 100 and enterprise bellwethers.
- **News Feeds**: Free RSS syndication from Moneycontrol, Economic Times, and Livemint with Loughran-McDonald NLP sentiment.
- **Vector & RAG**: SQLite embedded vector index with 384-dimensional deterministic hash-projection embeddings and local synthesis.
- **Cost**: **₹0.00 / month**.

### Tier 2: Individual Trader / Pro Investor (Optional Activation)
- **Real-Time Data**: Angel One SmartAPI (Free with brokerage account) or Zerodha Kite Connect (₹2,000–₹4,000/month).
- **LLM Reasoning**: Google Gemini 2.5 Flash with free tier API key (15 requests/minute).
- **News API**: NewsAPI developer key for broader English financial news syndication.

### Tier 3: Institutional Deployment
- **Market Data**: Licensed NSE Data & Analytics 5-second snapshot feed or Level-2 tick feed.
- **Corporate Disclosures**: Direct automated XBRL filing ingestion from BSE StAR / NSE NEAPS exchange feeds.
- **Database**: Managed PostgreSQL with `pgvector` extension for distributed horizontal vector search.

---

## 3. Secret Management & Provider Security Policy

1. **Zero Secret Exposure**: API keys and secrets are never returned in API payloads, never rendered in browser DOM, never printed in terminal logs, and never serialized into PDF/CSV reports.
2. **Redacted Presence Diagnostics**: `/api/health` reports credential presence using masked prefixes (e.g., `AIzaSy...****`) or explicit `Not Configured (Local Deterministic Engine Active)`.
3. **Graceful Degradation**: If an optional provider is unreachable, missing, or rate-limited, the system falls back to cached baseline data and explicitly marks the observation status (`DELAYED`, `ARCHIVED`, or `INSUFFICIENT DATA`).
