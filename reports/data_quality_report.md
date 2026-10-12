# BHARAT VALUE AI — Data Quality & Integrity Report
**Date:** October 10, 2026  
**Auditor:** Principal Financial Data Engineer  
**Scope:** Market Data Normalization, Accounting Unit Conventions, and Sanity Gates

---

## 1. Accounting Conventions and Unit Standards

To eliminate unit confusion across corporate disclosures and calculation modules, BHARAT VALUE AI strictly enforces the following institutional conventions:

1. **Monetary Units**:
   - Aggregate financial statements (Revenue, EBITDA, PAT, Debt, Cash Flow) are reported in **INR Crores (₹ Cr)** ($1\text{ Crore} = 10,000,000\text{ INR}$).
   - Per-share metrics (LTP, EPS, Book Value Per Share, Target Fair Value) are reported in **INR per share (₹)**.
   - Trading turnover is converted to **₹ Crores** ($\frac{\text{Price} \times \text{Volume}}{10^7}$).
2. **Reporting Basis**:
   - Financial statements consume **Consolidated Audited Accounts** by default, capturing operating subsidiaries and debt obligations.
   - For standalone-only entities (e.g. `CASTROLIND`, `HUDCO`), statements are explicitly labeled as `Standalone Audited`.
3. **Timezone Normalization**:
   - All internal event logs, quotes, and audit records store timezone-aware UTC datetimes.
   - All user-facing timestamps, reports, and API payloads display **India Standard Time (IST)** with the explicit format: `YYYY-MM-DD HH:MM:SS IST`.
4. **Exchange Ticker Normalization**:
   - The platform maps disparate aliases (e.g., "HDFC Bank", "HDFCBANK.NS", "500180") to canonical `NSE:<SYMBOL>` identifiers.

---

## 2. Market Data Quality & Anomaly Detection Gates

Every market quote and historical candle must pass the `MarketDataQualityValidator` before being persisted or consumed:

| Validation Gate | Rule Formula | Severity | Action on Failure |
|---|---|---|---|
| **High Boundary** | $\text{High} \ge \max(\text{Open}, \text{Low}, \text{Close})$ | **CRITICAL** | Candle rejected; excluded from analysis. |
| **Low Boundary** | $\text{Low} \le \min(\text{Open}, \text{High}, \text{Close})$ | **CRITICAL** | Candle rejected; excluded from analysis. |
| **Non-Negative Price** | $\text{Open}, \text{High}, \text{Low}, \text{Close} > 0$ | **CRITICAL** | Replaced with error diagnostic; never rendered. |
| **Non-Negative Volume** | $\text{Volume} \ge 0$ | **WARNING** | Volume floored to 0; warning logged. |
| **Extreme Price Jump** | $\left\|\frac{\text{Close} - \text{PrevClose}}{\text{PrevClose}}\right\| > 30\%$ | **WARNING** | Flagged as circuit filter breach or potential unadjusted stock split. |
| **Quote Staleness** | $\text{Age} > 72\text{ hours}$ | **INFO** | Labeled as weekend or exchange holiday observation. |

---

## 3. Negative Earnings and Division-by-Zero Handling

Historical financial statements for turnarounds or loss-making cyclical smallcaps often feature negative operating profit, negative net income, or zero shares outstanding. The engine enforces the following mathematical safeguards:

1. **Negative PAT / EPS**:
   - If $\text{EPS} \le 0$, the Price-to-Earnings ratio ($\text{P/E}$) is **NEVER** reported as a negative multiple (e.g., $-15.0\text{x}$ is economically meaningless and misleads retail investors).
   - The ratio is marked `None` / `Not Applicable (Loss-making)`, and valuation shifts to book-value, sales, or normalized cash-flow approaches with an explicit warning note.
2. **Negative Free Cash Flow**:
   - In DCF valuation, if baseline FCF is negative, Gordon Growth projection cannot be applied blindly. The system issues an explicit limitation warning and falls back to normalized operating margins or book-value metrics.
3. **Division-by-Zero Protection**:
   - When Total Assets, Total Equity, or Revenue are zero or negative, DuPont decomposition safely returns zero margin and zero asset turnover with `interpretation: "Insufficient verified data to decompose Return on Equity."`

---

## 4. Non-Fabrication Policy & Quote Status Badges

In strict adherence to institutional standards:
- **No Synthetic Candles**: The previous `_generate_fallback_candles` (which produced synthetic sine waves when offline) has been completely removed.
- **Explicit Quote Status**: Every quote is tagged with one of five transparent states:
  1. `LIVE`: Provider confirmed real-time execution during regular market hours (09:15 to 15:30 IST).
  2. `DELAYED`: Provider supplies delayed quotes (standard 15-minute exchange delay).
  3. `LAST AVAILABLE`: Outside market hours (weekends/holidays) or when the upstream provider is unreachable, displaying the last verified historical observation with exact timestamp.
  4. `DEMO`: Only displayed when the user explicitly toggles Demo Sandbox mode in platform settings.
  5. `UNAVAILABLE`: Returned when no quote can be retrieved. The UI displays an honest empty state with explanation.

---

## 5. Point-in-Time Regulatory Filing Discipline

To avoid look-ahead bias in research and backtesting:
- The `PointInTimeEngine` enforces a 45-day statutory window after quarter end (aligned with SEBI quarterly disclosure deadlines) before financial figures become eligible for historical backtests or ranking models.

---
*End of Data Quality & Integrity Report.*
