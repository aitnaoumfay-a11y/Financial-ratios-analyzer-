# Financial-ratios-analyzer-
Reusable Python module — 12 financial ratios, Moroccan sector benchmarks, weighted health score, radar chart and bar chart. Validated on Label Vie, Cosumar, CIH Bank.
# Financial Ratio Analyzer 📊

**A reusable Python module for financial ratio analysis and benchmarking**

> Validated on Moroccan listed companies — Label Vie, Cosumar, CIH Bank  
> FSJES Marrakech — Centre d'Excellence | Applied Finance

---

## Overview

A clean, modular Python tool that computes, benchmarks, and visualises **financial ratios** from balance sheet and income statement inputs. Built for financial analysts working on Moroccan listed and unlisted companies.

---

## Features

- **12 financial ratios** across 3 categories (liquidity, leverage, profitability)
- **Sector benchmarking** against Moroccan industry medians (Distribution, Banques, Agroalimentaire, BTP)
- **Weighted health score** (0–100) calibrated for credit analysis
- **Radar chart** — normalised ratio profile vs benchmark
- **Bar chart** — company vs sector benchmark, colour-coded by signal
- **Multi-company comparison** chart
- **Console report** with ✓ / ~ / ✗ signal indicators

---

## Ratios computed

### Liquidity
| Ratio | Formula |
|---|---|
| Current ratio | Current assets / Current liabilities |
| Quick ratio | (Current assets − Inventory) / Current liabilities |
| Cash ratio | Cash / Current liabilities |

### Leverage
| Ratio | Formula |
|---|---|
| Debt-to-equity | Total debt / Total equity |
| Debt ratio | Total debt / Total assets |
| Equity ratio | Total equity / Total assets |
| Interest coverage | EBIT / Interest expense |

### Profitability
| Ratio | Formula |
|---|---|
| Gross margin | Gross profit / Revenue × 100 |
| Net margin | Net income / Revenue × 100 |
| ROE | Net income / Total equity × 100 |
| ROA | Net income / Total assets × 100 |

---

## Usage

```python
from financial_ratio_analyzer import FinancialAnalyzer

fa = FinancialAnalyzer(
    data={
        "current_assets":      3_850_000,
        "current_liabilities": 3_100_000,
        "inventory":           1_200_000,
        "cash":                  420_000,
        "total_debt":          2_800_000,
        "total_equity":        2_100_000,
        "ebit":                  310_000,
        "interest_expense":       90_000,
        "revenue":            14_200_000,
        "gross_profit":        2_980_000,
        "net_income":            580_000,
        "total_assets":        7_100_000,
    },
    company_name="Label Vie",
    sector="Distribution",   # Distribution | Banques | Agroalimentaire | BTP
    year=2023,
)

fa.compute_all()
fa.report()       # console table with signals
fa.bar_chart()    # ratios vs benchmark bar chart
fa.radar_chart()  # normalised profile radar
```

**Compare multiple companies:**
```python
from financial_ratio_analyzer import compare_companies
compare_companies([fa_label_vie, fa_cosumar, fa_cih_bank])
```

---

## Demo output — Label Vie 2023

```
============================================================
  FINANCIAL RATIO REPORT — LABEL VIE
  Sector : Distribution  |  Year : 2023
============================================================
  LIQUIDITY
  current_ratio               1.24      1.20        ✓
  quick_ratio                 0.85      0.70        ✓

  LEVERAGE
  debt_to_equity              1.33      1.50        ✓
  interest_coverage           3.44      3.00        ✓

  PROFITABILITY
  net_margin_pct              4.08      3.50        ✓
  roe_pct                    27.62     10.00        ✓
  roa_pct                     8.17      4.00        ✓

  HEALTH SCORE : 85.5/100
============================================================
```

---

## Requirements

```
pandas >= 1.5
numpy >= 1.23
matplotlib >= 3.6
```

```bash
pip install pandas numpy matplotlib
python financial_ratio_analyzer.py   # runs demo on Label Vie, Cosumar, CIH Bank
```

---
