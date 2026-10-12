# BHARAT VALUE AI — Financial Model Validation Report
**Date:** October 10, 2026  
**Auditor:** Quantitative Financial Model Auditor & Equity Analyst  
**Scope:** Valuation Engines, Sector-Appropriate Routing, and Stress Sensitivity

---

## 1. Executive Summary

Financial valuation models must strictly reflect the economic reality of the underlying industry. Applying manufacturing debt/equity or enterprise value metrics indiscriminately to banking institutions is a critical financial error commonly found in naive retail dashboards.

This document validates the two decoupled mathematical valuation branches implemented in `bharat_value_ai/analysis/fair_value.py`:
1. **Branch A**: Free Cash Flow DCF & Multiples (Non-Financial / Industrial / IT / EPC / Consumer).
2. **Branch B**: Residual Income & Justified P/B Models (Banks, NBFCs, and Lending Institutions).

---

## 2. Sector-Appropriate Valuation Architecture

```
                          ┌───────────────────────────┐
                          │   Company Universe Ticker │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                        Is Company a Bank or NBFC?
                                        │
                    ┌───────────────────┴───────────────────┐
                    │ YES                                   │ NO
                    ▼                                       ▼
    ┌───────────────────────────────┐       ┌───────────────────────────────┐
    │   BRANCH B: BANKING / NBFC    │       │     BRANCH A: INDUSTRIALS     │
    │  - Residual Income Model (RIM)│       │  - Discounted Cash Flow (DCF) │
    │  - Justified P/B (ROE vs Ke)  │       │  - EV/EBITDA Relative Value   │
    │  - Banking P/E Multiple       │       │  - Smallcap P/E Multiple      │
    │                               │       │                               │
    │  * NO Net Debt Subtraction    │       │  * Net Debt = Debt - Cash     │
    │  * NO EV/EBITDA Applied       │       │  * WACC Discount Rate         │
    └───────────────┬───────────────┘       └───────────────┬───────────────┘
                    │                                       │
                    ▼                                       ▼
            Composite Value                         Composite Value
           (40% RIM + 40% P/B                      (50% DCF + 30% P/E
               + 20% P/E)                             + 20% EV/EBITDA)
```

---

## 3. Mathematical Specifications

### 3.1 Non-Financial DCF Valuation (Branch A)

For eligible non-financial companies, enterprise cash flows are projected over a 5-year explicit horizon and discounted by the Weighted Average Cost of Capital ($\text{WACC}$):

$$\text{PV}(\text{FCF}) = \sum_{t=1}^n \frac{\text{FCF}_0 \times (1 + g)^t}{(1 + \text{WACC})^t}$$

Terminal Value ($\text{TV}$) is calculated using the Gordon Growth Model:

$$\text{TV} = \frac{\text{FCF}_n \times (1 + g_{\text{terminal}})}{\text{WACC} - g_{\text{terminal}}}$$

$$\text{Enterprise Value} = \sum_{t=1}^n \text{PV}(\text{FCF}_t) + \frac{\text{TV}}{(1 + \text{WACC})^n}$$

$$\text{Equity Value} = \text{Enterprise Value} - \text{Net Debt} \quad (\text{where Net Debt} = \text{Total Debt} - \text{Cash})$$

$$\text{Fair Value Per Share} = \frac{\text{Equity Value}}{\text{Shares Outstanding}}$$

**Validation Check**: If $\text{WACC} \le g_{\text{terminal}}$, the model raises a strict `ValueError` to prevent negative or infinite terminal values.

---

### 3.2 Banking & NBFC Valuation (Branch B)

#### Why Standard DCF & EV/EBITDA Fail for Banks:
1. **Deposits are Raw Materials**: In a bank, customer deposits and borrowings are the operational inputs used to fund loans (interest-earning assets). Treating customer deposits as "debt" to subtract from Enterprise Value drastically understates equity value and yields nonsensical negative valuations.
2. **Interest Expense is Operating COGS**: For a bank, interest paid is the cost of goods sold. Operating profit (EBITDA) is meaningless because interest expense cannot be added back.

#### Method 1: Justified Price-to-Book (Justified P/B)
Sustainable Return on Equity ($\text{ROE}$) is compared against the Cost of Equity ($K_e$):

$$\text{Justified P/B} = \frac{\text{ROE} - g}{K_e - g}$$

$$\text{Fair Value}_{\text{JPB}} = \text{Justified P/B} \times \text{Book Value Per Share}$$

*Baseline Parameters for Indian Banks*:
- $K_e = 12.5\%$ (Risk-free rate $6.8\%$ + Indian Banking Beta $1.0 \times \text{ERP } 5.7\%$)
- $g = 5.0\%$ (Long-term Indian nominal GDP sustainable growth anchor)

#### Method 2: Residual Income Model (RIM)
Calculates value created in excess of the cost of equity over book value:

$$\text{Equity Value} = \text{BV}_0 + \sum_{t=1}^5 \frac{(\text{ROE} - K_e) \times \text{BV}_{t-1}}{(1 + K_e)^t} + \frac{(\text{ROE} - K_e) \times \text{BV}_5}{(K_e - g) \times (1 + K_e)^5}$$

---

## 4. Scenario & Sensitivity Analysis

Each valuation automatically generates:
1. **Bear Case**:
   - Industrials: Revenue growth reduced by $30\%$, $\text{WACC} + 1.5\%$, terminal growth $4.0\%$.
   - Banks: $\text{ROE}$ compressed by $250\text{ bps}$, $K_e$ elevated to $14.0\%$.
2. **Base Case**: Composite weighted modeled valuation.
3. **Bull Case**:
   - Industrials: Revenue growth expanded by $25\%$, $\text{WACC} - 1.0\%$, terminal growth $5.5\%$.
   - Banks: $\text{ROE}$ expanded by $250\text{ bps}$, $K_e$ lowered to $11.5\%$.
4. **Sensitivity Matrix**:
   - Non-financials: $5 \times 4$ grid evaluating $\text{WACC } (10\% - 14\%)$ vs $g_{\text{terminal }} (3\% - 6\%)$.
   - Banks: $5 \times 5$ grid evaluating Cost of Equity $K_e (11\% - 15\%)$ vs sustainable $\text{ROE } (\pm 4\%)$.

---

## 5. Margin of Safety Formula & Decision Thresholds

$$\text{Margin of Safety (\%)} = \frac{\text{Composite Fair Value} - \text{Current Market Price}}{\text{Current Market Price}} \times 100$$

| Margin of Safety Range | Platform Classification | Plain English Meaning |
|---|---|---|
| $> +15.0\%$ | **UNDERVALUED** | Trading at a modeled discount to estimated intrinsic value. |
| $-15.0\%$ to $+15.0\%$ | **FAIRLY_VALUED** | Market price roughly reflects underlying fundamentals. |
| $< -15.0\%$ | **OVERVALUED** | Trading at a modeled premium to estimated intrinsic value. |

---
*End of Financial Model Validation Report.*
