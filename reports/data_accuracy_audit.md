# BHARAT VALUE AI — Financial Data Accuracy & Formula Audit
**Audit Date:** October 11, 2026  
**Auditor:** Quantitative Financial Engineer & Financial Model Auditor  
**Document Target:** `reports/data_accuracy_audit.md`  

---

## 1. Executive Summary

A comprehensive financial-model audit was conducted across all pricing adapters, ratio calculations, sector valuation models, quality metrics, and governance risk rules in `bharat_value_ai`. 

The core directive of the platform is:  
**"Never fabricate prices, financial figures, historical candles, news articles, or source timestamps. Never substitute zero or arbitrary positive defaults for unavailable data unless zero is the actual verified value."**

While previous patches eliminated crashes on banking stocks and ensured test pass rates, this audit identifies specific areas where silent defaults, unvalidated inputs, or legacy fallback dictionaries remain in production code.

---

## 2. Market Data Accuracy & Status Taxonomy

### 2.1 Current Implementation vs Institutional Target

Currently, `bharat_value_ai/data/normalization.py` defines:
```python
class QuoteStatus(str, Enum):
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    LAST_AVAILABLE = "LAST AVAILABLE"
    DEMO = "DEMO"
    UNAVAILABLE = "UNAVAILABLE"
```

To meet institutional standards, the market-data contract must support the full explicit taxonomy:
1. `LIVE_VERIFIED`: Real-time streaming or tick data directly verified from exchange feed (only during market hours 09:15-15:30 IST on authorized feeds).
2. `DELAYED_VERIFIED`: Legitimate 15-minute delayed quotes from authorized exchange distributors (e.g. Yahoo Finance `.NS` feed).
3. `HISTORICAL_VERIFIED`: Last closing price from audited bhavcopy archives when market is closed or offline.
4. `CACHED_STALE`: Observation retained in local cache whose TTL has expired but no fresh quote could be fetched.
5. `UNAVAILABLE`: Upstream provider unreachable, symbol not traded, or zero volume without valid quote.
6. `INVALID`: Malformed symbol, negative prices, impossible high/low boundaries, or data corruption.

### 2.2 Canonical Price Parity Audit
- **Finding:** In previous iterations, different screens independently fetched prices from varying sources (e.g. DCF calculator calling `market_provider.get_quote()`, Details calling `/api/market/quote`, and Summary calling `SnapshotService`).
- **Resolution:** All downstream consumers (`fair_value.py`, `quality_growth.py`, `orchestrator.py`, `generator.py`) must consume the immutable `SnapshotService.get_snapshot(symbol)` to guarantee strict parity across every screen.

---

## 3. Financial Calculation Formulas & Missing-Data Policies

Below is the definitive formula catalog, reporting periods, units, and missing-data policies for all platform metrics:

### 3.1 Market Ratios & Multiples
| Metric | Mathematical Formula | Reporting Period / Inputs | Units | Missing-Data Policy |
|---|---|---|---|---|
| **Last Traded Price (LTP)** | Direct exchange execution price | Real-time or 15m delayed | INR (₹) | Never default to 0.0 unless traded at 0. Return `UNAVAILABLE`. |
| **Change & % Change** | `Change = Price - PrevClose`<br>`% Change = (Change / PrevClose) * 100` | Current trading session vs. previous official close | INR (₹) & % | If `PrevClose` is missing or `<= 0`, return `None` (do not display 0.00% gain). |
| **Market Capitalization** | `Price * Shares Outstanding` | Current Price & Audited Share Capital | INR Crores | Return `None` if shares or price unavailable. |
| **Price-to-Earnings (P/E)** | `Current Price / TTM Diluted EPS` | Trailing Twelve Months (TTM) or latest audited FY | Ratio (x) | If `EPS <= 0`, return `N/A (Loss-making)`. Never display negative P/E or division-by-zero. |
| **Price-to-Book (P/B)** | `Current Price / Book Value per Share` | Latest Audited Balance Sheet | Ratio (x) | If `BVPS <= 0`, return `N/A (Negative Net Worth)`. |
| **EV / EBITDA** | `(Market Cap + Total Debt - Cash) / EBITDA` | Industrial companies only | Ratio (x) | **Excluded for Banks/NBFCs**. Return `N/A` if EBITDA `<= 0`. |

---

### 3.2 Operating & Profitability Ratios
| Metric | Mathematical Formula | Reporting Period | Units | Missing-Data Policy |
|---|---|---|---|---|
| **Gross Margin %** | `((Revenue - COGS) / Revenue) * 100` | Audited Annual / TTM | % | Return `None` if Revenue `<= 0`. |
| **Operating Margin %** | `(Operating Profit / Revenue) * 100` | Audited Annual / TTM | % | Return `None` if Revenue `<= 0`. |
| **Net Profit Margin %** | `(Net Profit / Revenue) * 100` | Audited Annual / TTM | % | Return `None` if Revenue `<= 0`. |
| **Return on Equity (ROE)** | `(Net Profit / Average Total Equity) * 100` | Audited Annual | % | Return `None` if Total Equity `<= 0`. |
| **Return on Capital Employed (ROCE)** | `(EBIT / (Total Assets - Current Liabilities)) * 100` | Audited Annual | % | **Excluded for Banks/NBFCs**; return `None` if Capital Employed `<= 0`. |
| **DuPont 3-Stage ROE** | `NPM * Asset Turnover * Equity Multiplier`<br>`= (PAT/Sales) * (Sales/Assets) * (Assets/Equity)` | Audited Annual | Decomposition | If any of Sales, Assets, or Equity are `None` or `<= 0`, return `Insufficient verified data`. |

---

### 3.3 Cash Flow & Leverage Ratios
| Metric | Mathematical Formula | Reporting Period | Units | Missing-Data Policy |
|---|---|---|---|---|
| **Operating Cash Flow (OCF)** | Audited Cash Flow from Operations | Audited Annual | INR Crores | Return `None` if uncatalogued. |
| **Free Cash Flow (FCF)** | `OCF - Capital Expenditures (Capex)` | Audited Annual | INR Crores | **Excluded for Banks/NBFCs**. Return `None` if uncatalogued. |
| **Debt-to-Equity (D/E)** | `Total Borrowings / Total Shareholder Equity` | Audited Balance Sheet | Ratio | **Excluded for Banks/NBFCs** (deposits are not debt). Return `None` if equity `<= 0`. |
| **Interest Coverage Ratio** | `EBIT / Finance Costs` | Audited Profit & Loss | Ratio (x) | **Excluded for Banks/NBFCs**. Return `None` if Finance Costs `<= 0`. |
| **Altman Z-Score** | `1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5` | Audited Balance Sheet & P&L | Score | **Industrials only**. Return `None` if assets or liabilities are missing. |

---

### 3.4 Banking & NBFC Specific Metrics (BFSI Sector)
| Metric | Mathematical Formula | Regulatory Standard | Units | Missing-Data Policy |
|---|---|---|---|---|
| **Net Interest Margin (NIM)** | `(Interest Income - Interest Expended) / Average Earning Assets` | RBI Master Direction | % | Mandatory for Banks. Return `None` if uncatalogued. |
| **Gross NPA (GNPA %)** | `(Gross Non-Performing Assets / Gross Advances) * 100` | RBI Asset Classification | % | Benchmarked at `< 3.0%` for quality banks. Return `None` if uncatalogued. |
| **Net NPA (NNPA %)** | `(Net Non-Performing Assets / Net Advances) * 100` | RBI Asset Classification | % | Benchmarked at `< 1.0%`. Return `None` if uncatalogued. |
| **Capital Adequacy (CRAR %)** | `(Tier 1 Capital + Tier 2 Capital) / Risk-Weighted Assets` | Basel III Guidelines | % | Regulatory minimum `11.5%`. Return `None` if uncatalogued. |
| **CASA Ratio %** | `((Current Deposits + Savings Deposits) / Total Deposits) * 100` | RBI Banking Statistics | % | Quality benchmark `> 40%`. Return `None` if uncatalogued. |

---

## 4. Confirmed Silent-Default Defects Discovered in Audit

### Defect 1: Valuation Engine Industrial Branch Defaults (`fair_value.py` L268-278)
```python
# CURRENT FLAWED IMPLEMENTATION:
net_profit = fundamentals.get("net_profit") or 100.0
ebitda = fundamentals.get("operating_profit") or (net_profit * 1.5)
debt = fundamentals.get("total_debt") or 0.0
cash = fundamentals.get("cash_and_equivalents") or 0.0
fcf = fundamentals.get("free_cash_flow") or (net_profit * 0.8)
shares_cr = (net_profit / eps) if eps > 0 else 10.0
```
- **Severity:** CRITICAL
- **Impact:** If an uncatalogued stock (e.g. `NEWCO`) is requested, the system silently assumes it makes ₹100 Cr profit, generates ₹80 Cr free cash flow, and prints a fabricated Fair Value of ₹1,400+ rather than stating that data is unavailable.
- **Required Fix:** If `net_profit is None` or `fcf is None`, do NOT calculate DCF. Return a `ValuationResult` with `valuation_status="UNAVAILABLE"`, `composite_fair_value=None`, and explicit notes explaining that audited financial statements are missing.

### Defect 2: Quality Engine Pillar Defaults (`quality_growth.py` L23-45)
```python
# CURRENT FLAWED IMPLEMENTATION:
gm = fund.get("gross_margin_pct") if fund.get("gross_margin_pct") is not None else 30.0
npm = fund.get("net_margin_pct") if fund.get("net_margin_pct") is not None else 10.0
roce = fund.get("roce_pct") if fund.get("roce_pct") is not None else 15.0
roe = fund.get("roe_pct") if fund.get("roe_pct") is not None else 15.0
```
- **Severity:** HIGH
- **Impact:** Automatically awards uncatalogued stocks a 45+ "Fair Quality" score based on phantom margins and capital return metrics.
- **Required Fix:** If critical metrics are missing, return `composite_score=0.0`, `quality_tier="DATA_INSUFFICIENT"`, and omit misleading pillar awards.

---

## 5. Implementation Roadmap for Data Accuracy
1. Refactor `fair_value.py` to abort DCF and RIM calculations when core inputs (`net_profit`, `fcf`, `book_value_per_share`) are `None`.
2. Refactor `quality_growth.py` to require verified data before awarding scores.
3. Expand `QuoteStatus` in `normalization.py` to support `LIVE_VERIFIED`, `DELAYED_VERIFIED`, `HISTORICAL_VERIFIED`, `CACHED_STALE`, `UNAVAILABLE`, `INVALID`.
4. Ensure all PDF and CSV exports reflect the verified status and missing-data disclosures.
