# BHARAT VALUE AI — Financial Calculation & Valuation Engine Audit

**Audit Date:** October 12, 2026  
**Auditor:** Quantitative Researcher & Indian Equity Fundamental Analyst  
**Scope:** Independent Mathematical Verification of Financial Statements, DuPont Analysis, Altman Z-Score, Industrial DCF, and Banking Valuation Models.

---

## 1. 3-Stage DuPont Decomposition

### Mathematical Formula
$$\text{Return on Equity (ROE)} = \text{Net Profit Margin} \times \text{Asset Turnover} \times \text{Equity Multiplier}$$

$$\text{ROE} = \left(\frac{\text{Net Income}}{\text{Total Revenue}}\right) \times \left(\frac{\text{Total Revenue}}{\text{Total Assets}}\right) \times \left(\frac{\text{Total Assets}}{\text{Total Equity}}\right)$$

### Verification Benchmark: CDSL (FY2023-24 Consolidated Accounts)
- **Reported Net Income (PAT)**: ₹420.00 Cr
- **Reported Operating Revenue**: ₹905.00 Cr
- **Reported Total Assets**: ₹1,850.00 Cr
- **Reported Shareholders' Equity**: ₹1,520.00 Cr

### Independent Hand Calculation
1. **Net Profit Margin (NPM)**:
   $$\text{NPM} = \frac{420.00}{905.00} = 46.4088\% \approx 46.41\%$$
2. **Asset Turnover (AT)**:
   $$\text{AT} = \frac{905.00}{1850.00} = 0.489189\text{x} \approx 0.49\text{x}$$
3. **Equity Multiplier (Financial Leverage - EM)**:
   $$\text{EM} = \frac{1850.00}{1520.00} = 1.217105\text{x} \approx 1.22\text{x}$$
4. **Product Verification**:
   $$\text{ROE}_{\text{calc}} = 0.464088 \times 0.489189 \times 1.217105 = 0.276315 \approx 27.63\%$$
   $$\text{Direct ROE} = \frac{420.00}{1520.00} = 27.6315\%$$
   $$\text{Delta} = 0.0000\% \quad (\text{Exact Mathematical Identity Satisfied})$$

---

## 2. Altman Z-Score for Indian Non-Financial Corporations

### Mathematical Formula
$$Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$$
Where:
- $X_1 = \frac{\text{Working Capital}}{\text{Total Assets}}$
- $X_2 = \frac{\text{Retained Earnings}}{\text{Total Assets}}$
- $X_3 = \frac{\text{EBIT}}{\text{Total Assets}}$
- $X_4 = \frac{\text{Market Value of Equity}}{\text{Total Liabilities}}$
- $X_5 = \frac{\text{Sales / Revenue}}{\text{Total Assets}}$

### Verification Benchmark: Non-Financial Industrial Sample
- **Total Assets**: ₹10,000 Cr
- **Working Capital**: ₹2,500 Cr $\implies X_1 = 0.25$
- **Retained Earnings**: ₹4,000 Cr $\implies X_2 = 0.40$
- **EBIT**: ₹1,500 Cr $\implies X_3 = 0.15$
- **Market Cap**: ₹25,000 Cr; **Total Debt/Liabilities**: ₹5,000 Cr $\implies X_4 = 5.00$
- **Total Revenue**: ₹8,000 Cr $\implies X_5 = 0.80$

### Independent Hand Calculation
$$Z = 1.2(0.25) + 1.4(0.40) + 3.3(0.15) + 0.6(5.00) + 0.999(0.80)$$
$$Z = 0.300 + 0.560 + 0.495 + 3.000 + 0.7992 = 5.1542 \approx 5.15$$
**Zone Classification**: $Z > 2.99 \implies \text{Safe Zone (Negligible 2-Year Insolvency Risk)}$.  
**Engine Output**: $Z = 5.15$, Category = `SAFE_ZONE`. Exactly matches hand calculation.

---

## 3. Industrial Discounted Cash Flow (DCF) & Enterprise Value Waterfall

### Valuation Engine Rules
1. **Explicit 5-Year Projection Period**: Free Cash Flow to Firm ($\text{FCFF}_t = \text{FCFF}_0 \times (1 + g)^t$).
2. **Terminal Value (Gordon Growth)**:
   $$\text{TV}_5 = \frac{\text{FCFF}_5 \times (1 + g_{\text{terminal}})}{\text{WACC} - g_{\text{terminal}}}$$
3. **Discounting**:
   $$\text{PV}(\text{Explicit}) = \sum_{t=1}^5 \frac{\text{FCFF}_t}{(1 + \text{WACC})^t}, \quad \text{PV}(\text{TV}) = \frac{\text{TV}_5}{(1 + \text{WACC})^5}$$
4. **Enterprise Value to Equity Value Bridge**:
   $$\text{Enterprise Value (EV)} = \text{PV}(\text{Explicit}) + \text{PV}(\text{TV})$$
   $$\text{Equity Value} = \text{EV} - \text{Total Debt} + \text{Cash \& Cash Equivalents}$$
   $$\text{Intrinsic Fair Value per Share} = \frac{\text{Equity Value}}{\text{Shares Outstanding}}$$

### Verification Test: CDSL Baseline
- **FCFF Base**: ₹350.0 Cr
- **Growth Rate ($g$)**: 15.0%
- **Discount Rate ($\text{WACC}$)**: 12.0%
- **Terminal Growth ($g_{\text{terminal}}$)**: 5.0%
- **Net Debt**: -₹1,150.0 Cr (Net Cash)
- **Share Count**: 10.45 Cr shares

### Hand Calculation:
- $\text{FCFF}_1 = 350 \times 1.15 = 402.50 \implies \text{PV} = \frac{402.50}{1.12^1} = 359.38$
- $\text{FCFF}_2 = 402.50 \times 1.15 = 462.88 \implies \text{PV} = \frac{462.88}{1.12^2} = 369.00$
- $\text{FCFF}_3 = 462.88 \times 1.15 = 532.31 \implies \text{PV} = \frac{532.31}{1.12^3} = 378.89$
- $\text{FCFF}_4 = 532.31 \times 1.15 = 612.15 \implies \text{PV} = \frac{612.15}{1.12^4} = 389.04$
- $\text{FCFF}_5 = 612.15 \times 1.15 = 703.98 \implies \text{PV} = \frac{703.98}{1.12^5} = 399.45$
- **$\text{PV}(\text{Explicit})$** = ₹1,895.76 Cr
- $\text{TV}_5 = \frac{703.98 \times 1.05}{0.12 - 0.05} = \frac{739.18}{0.07} = 10,559.71 \text{ Cr}$
- **$\text{PV}(\text{TV})$** = $\frac{10,559.71}{1.12^5} = 5,991.88 \text{ Cr}$
- **Enterprise Value (EV)** = $1,895.76 + 5,991.88 = 7,887.64 \text{ Cr}$
- **Equity Value** = $7,887.64 - (-1,150.0) = 9,037.64 \text{ Cr}$
- **DCF Value per Share** = $\frac{9,037.64}{10.45} = ₹864.85$
- **Engine Verified Result**: Passes unit test `test_dcf_valuation_calculation`.

---

## 4. Banking & Financial Valuation: Residual Income (RIM) & Justified P/B

### Sector Constraint
Commercial banks and NBFCs treat debt as raw material (deposits and borrowings) rather than capital structure leverage. Standard Free Cash Flow to Firm (FCFF) and EV/EBITDA models produce mathematically meaningless results for banking entities.

### Residual Income Model (RIM)
$$\text{Fair Value} = \text{Book Value per Share (BVPS)}_0 + \sum_{t=1}^5 \frac{\text{ROE}_t - K_e}{(1 + K_e)^t} \times \text{BVPS}_{t-1} + \frac{(\text{ROE}_{\text{term}} - K_e) \times \text{BVPS}_5}{(K_e - g) \times (1 + K_e)^5}$$
Where $K_e$ is Cost of Equity derived via Capital Asset Pricing Model ($K_e = R_f + \beta \times \text{ERP}$).

### Justified Price-to-Book (P/B)
$$\text{Target P/B} = \frac{\text{Sustainable ROE} - g}{K_e - g}$$
For ICICI Bank ($\text{ROE} = 18.5\%$, $K_e = 12.5\%$, $g = 6.0\%$):
$$\text{Target P/B} = \frac{0.185 - 0.060}{0.125 - 0.060} = \frac{0.125}{0.065} = 1.923\text{x}$$
With BVPS of ₹350.00:
$$\text{Justified Value per Share} = 350.00 \times 1.923 = ₹673.05$$
**Engine Status**: Properly routed for ICICIBANK, SBIN, HDFCBANK, AXISBANK, and KOTAKBANK in `fair_value_engine`.

---

## 5. Missing Data & Insufficient Evidence Guardrails

When a stock is uncatalogued or has unverified financial statements:
1. `fair_value_engine` returns `composite_fair_value = 0.0`, `valuation_status = "INSUFFICIENT_DATA"`.
2. Margin of safety calculation requires `current_price > 0` and verified inputs; otherwise returns `0.0`.
3. Frontend suppresses numerical values and renders `INSUFFICIENT DATA` badges and `--` placeholders.
