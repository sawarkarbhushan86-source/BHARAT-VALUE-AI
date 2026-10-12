# BHARAT VALUE AI — UI/UX Design & Usability Audit
**Audit Date:** October 11, 2026  
**Auditor:** Senior SaaS UI/UX Designer & Fintech Frontend Architect  
**Document Target:** `reports/ui_ux_audit.md`  

---

## 1. Executive Summary

A deep usability, visual hierarchy, and frontend architecture audit was conducted on the BHARAT VALUE AI web application (`bharat_value_ai/ui/templates/index.html`, `static/js/app.js`, and `static/css/style.css`).

The platform has a sleek dark aesthetic (slate/navy palette with vibrant cyan and emerald accents) and responsive Plotly charting. However, its current layout suffers from **feature fragmentation**: the application displays **14 top-level navigation items**, forcing users to jump between 6 different screens just to analyze a single stock (e.g. Details ➔ Fundamentals ➔ Valuation ➔ Quality ➔ Risk ➔ News).

To achieve institutional-grade SaaS maturity, the UI must be reorganized into a cohesive **7-section primary workspace** with an optional **Advanced Research Lab** for specialized quantitative and AI tools.

---

## 2. Current Navigation Structure vs Modernized Hierarchy

### 2.1 Current Fragmented Structure (14 Top-Level Items)
```
[Sidebar Root Menu]
├── Core Intelligence
│   ├── Market Overview (view-market)
│   ├── Stock Screener (view-screener)
│   ├── Stock Details (view-details)
│   └── Fundamental Analysis (view-fundamentals)
├── Valuation & Growth
│   ├── Fair-Value Calculator (view-valuation)
│   ├── Quality & Multibagger (view-growth)
│   └── Risk & Governance (view-risk)
├── News & NLP Engine
│   ├── Financial News Feed (view-news)
│   ├── News-to-Price Events (view-timeline)
│   └── NLP & FinBERT Lab (view-nlp)
├── AI & Agentic Research
│   ├── RAG Research Assistant (view-rag)
│   └── Multi-Agent Workflow (view-agents)
├── Quantitative Lab
│   ├── ML Stock Ranking (view-ml)
│   └── Strategy Backtesting (view-backtest)
└── Exports & Platform
    ├── Research Reports (view-reports)
    ├── API & System Health (view-health)
    └── Platform Settings (view-settings)
```

### 2.2 Usability Problems Identified in Current Layout
1. **Context Loss During Research:** When a user selects `CDSL` in Stock Details and then clicks "Fair-Value Calculator", the application does not clearly communicate that the valuation applies to the same active stock, requiring duplicate selections.
2. **Scatteration of Core Fundamentals:** DuPont Analysis, Solvency Ratios, Valuation Scenarios, and Risk Flags belong to a single company research workflow, yet they are separated into 4 distinct views.
3. **Overwhelming Cognitive Load for Beginners:** An ordinary investor is greeted with 14 competing tabs, making it unclear where to start.
4. **Redundant Search Bars & Dropdowns:** Global search exists in the topbar, yet individual views (Valuation, Quality, Timeline) duplicate dedicated ticker dropdowns.
5. **Watchlist & Portfolio Gap:** The platform has no watchlist or saved portfolio view, leaving users unable to track stocks they have analyzed.

---

## 3. Recommended Consolidated Navigation & Layout

To align with modern financial platforms (such as Koyfin, Trendlyne, and Bloomberg Terminal), the navigation is rationalized into **Primary Core Research** and an **Advanced Research Lab**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRIMARY NAVIGATION BAR                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. 📊 Overview           - Market snapshot, benchmark indices, news    │
│ 2. 🔍 Stock Screener      - Multi-metric filtering, sorting, universe   │
│ 3. 🏢 Company Research    - UNIFIED 360° HUB (Details + Fundamentals   │
│                            + Valuation + Risk + 10-Point Summary)      │
│ 4. 📑 Financial Analysis  - Deep DuPont, Solvency, Ratio Comparison    │
│ 5. 📰 News & Events       - NewsAPI live stream, filings, event timing │
│ 6. ⭐ Watchlist           - Browser-persistent pinned stocks           │
│ 7. 📥 Research Reports    - Institutional PDF & CSV exports            │
├────────────────────────────────────────────────────────────────────────┤
│                     ADVANCED RESEARCH LAB (Collapsible)                │
├────────────────────────────────────────────────────────────────────────┤
│ • 💬 RAG Assistant        - Evidence-grounded regulatory filing Q&A    │
│ • 🤖 Multi-Agent Workflow - 6-Agent institutional consensus engine     │
│ • 🧬 ML Alpha Ranking     - Cross-sectional models with uncertainty    │
│ • 📉 Strategy Backtesting - Walk-forward simulation with STT/brokerage │
├────────────────────────────────────────────────────────────────────────┤
│                     PLATFORM & SYSTEM HEALTH                           │
├────────────────────────────────────────────────────────────────────────┤
│ • ⚙️ Settings & Diagnostics - NewsAPI status, Gemini key, Cache purge  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed View-by-View UX Audit

### 4.1 Overview (Dashboard)
- **Strengths:** Clean grid displaying Nifty 50, Sensex, Nifty Smallcap 100, and market session indicator.
- **Deficiencies:** News feed on overview is limited to small cards without direct publisher links or NewsAPI provider status.
- **Improvement:** Embed NewsAPI connection indicator pill ("NewsAPI: Connected (38 articles indexed)") in dashboard header; show active top gainers/losers with verified source attribution.

### 4.2 Stock Screener
- **Strengths:** Interactive filtering sliders (Min ROCE, Max P/E, Min Revenue Growth) with table updates.
- **Deficiencies:** Table columns lack clear units (e.g. ₹ Cr vs %). Clicking a row did not immediately route to the comprehensive company profile.
- **Improvement:** Add "Research" quick action button in each row navigating straight to the Unified Company Research Hub. Format Indian currency figures consistently.

### 4.3 Unified Company Research Hub (The Major Innovation)
- **Concept:** Unify `view-details`, `view-fundamentals`, `view-valuation`, `view-growth`, and `view-risk` into a single organized workspace with sub-tabs or structured cards:
  - **Header:** Canonical symbol, verified LTP, IST timestamp, quote status badge (`LAST AVAILABLE`, `DELAYED_VERIFIED`), 52W range bar, Quick PDF Export button.
  - **Tab 1: 10-Point Investment Summary:** Beginner-friendly plain English summary, horizon selector (1-3M, 1-3Y, 3-5Y), and 4 interactive educational metric drawers.
  - **Tab 2: Valuation & Fair Value:** DCF/RIM intrinsic value, margin of safety gauge, bull/bear/base scenarios, sensitivity matrix.
  - **Tab 3: Financials & DuPont:** 3-stage DuPont decomposition, P&L / Balance Sheet highlights, capital efficiency.
  - **Tab 4: Quality & Moat:** 5-pillar scorecard with evidence weights.
  - **Tab 5: Governance & Risks:** Forewarning flags, promoter pledge checks, banking asset quality indicators.
  - **Tab 6: Related News:** Company-specific news articles from NewsAPI and exchange disclosures.

### 4.4 News & Events
- **Strengths:** Deduplication clustering and sentiment tags work well.
- **Deficiencies:** Missing clear visual distinction between statutory exchange filings (SEBI/BSE/NSE) and media stories (NewsAPI, ET).
- **Improvement:** Add badge filtering: `[All] [Official Filings] [Market Media] [Company Specific]`. Display publisher logo/name, publication time vs fetch time, and canonical article hyperlink.

### 4.5 Watchlist (New Recommended Feature)
- **Status:** Unimplemented in backend database.
- **Lightweight Solution:** Implement browser-based `localStorage` pinned stocks list with real-time price updates from `SnapshotService`, allowing investors to star stocks from the screener or details page without requiring backend auth.

---

## 5. Visual, Typography & Accessibility Standards

1. **Color Contrast & Readability:**
   - Background: Dark slate `#0f172a` and card surface `#1e293b`.
   - Primary text: High-contrast off-white `#f8fafc` (exceeds WCAG AAA standard).
   - Accents: Institutional emerald `#10b981` (bullish/safe), crimson `#ef4444` (bearish/risk), amber `#f59e0b` (warning/delayed), and royal blue `#3b82f6` (primary brand).
2. **Indian Number Formatting:**
   - Standardize all values into Indian numbering conventions:
     - `₹ 16,512.5 Cr` (Crores)
     - `₹ 45.2 Lakh` (Lakhs)
     - Avoid Western notations (e.g. `$1.2B`) that confuse Indian equity investors.
3. **Mobile & Tablet Responsiveness:**
   - Implement responsive collapsible sidebar with hamburger toggle on viewports `< 1024px`.
   - Wrap financial tables in horizontally scrollable containers (`overflow-x: auto`) with sticky ticker headers.
