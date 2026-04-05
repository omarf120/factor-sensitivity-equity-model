# Stock Selection Project  
**Quantitative Equity Factor Research Pipeline (CRSP × Compustat)**  

## Overview  
This project builds an end-to-end quantitative equity research pipeline using CRSP and Compustat data. The goal is to construct fundamental signals, clean financial data, and evaluate predictive power using Information Coefficient (IC) analysis across multiple horizons.

The pipeline mirrors institutional quant workflows, including data engineering, feature construction, and statistical validation.

---

## Key Features  

- **CRSP–Compustat Integration**
  - PERMNO–GVKEY linking
  - Point-in-time merge using `merge_asof` to avoid lookahead bias  

- **Robust Data Cleaning**
  - Outlier handling via truncation and winsorization  
  - Configurable thresholds (inner vs outer bounds)  
  - Flexible missing data handling  

- **Factor Construction**
  - Book-to-Price (B/P)  
  - Earnings-to-Price (E/P)  
  - Cash Flow-to-Price (CF/P)  
  - Sales-to-Price (S/P)  
  - ROA, ROE, CF/Sales  

- **Weekly Panel Construction**
  - Frequency: W-WED  
  - Adjusted prices using CRSP factors  
  - Dividend-adjusted total returns  

- **Forward Returns**
  - Horizons: 4, 8, 12, 24, 36, 48 weeks  
  - Log returns computed from t+1 to t+h  
  - Proper alignment to avoid lookahead bias  

- **IC Analysis**
  - Pearson IC  
  - Rank IC (Spearman)  
  - Metrics:
    - Mean IC  
    - t-statistics  
    - Hit rate  
    - Average cross-sectional coverage  

---

## Project Structure

## Project Structure

```
Stock Selection Project/
├── README.md
├── requirements.txt
├── configs/
│   └── config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── src/
│   ├── run_pipeline.py
│   ├── cleaning.py
│   ├── features.py
│   ├── compute_ic.py
│   └── utils.py
├── outputs/
│   ├── figures/
│   ├── tables/
│   │   ├── ic_series/
│   │   └── ic_all.csv
│   └── logs/
├── notebooks/
└── reports/
```


---

## Methodology  

### Data Processing  
- Adjusted price: `adj_prc = |PRC| * CFACPR`  
- Dividend alignment via `PAYDT` using `merge_asof`  
- Weekly aggregation with forward-filled prices  

### Factor Engineering  
- Price-scaled valuation ratios  
- Profitability metrics  
- Cash flow-based signals  
- Two-stage outlier handling:
  - Outer bounds → truncate  
  - Inner bounds → winsorize  

### Forward Returns  
- Computed using log returns  
- Non-overlapping windows  
- No lookahead bias  

### IC Evaluation  
- Cross-sectional IC computed each period  
- Aggregated into time-series statistics  
- Statistical significance assessed via t-stats  

---

## Results (Summary)  

- **Value factors (B/P)**  
  - Negative ICs increasing in magnitude at longer horizons  
  - Statistically significant  

- **Profitability (ROA, ROE)**  
  - Positive ICs  
  - Strength increases with horizon  
  - High hit rates  

- **Cash flow efficiency (CF/Sales)**  
  - Stable positive predictive power  

---

## How to Run  

### Install dependencies  
```bash
pip install -r requirements.txt
```

### Run Full Pipeline
```bash
python -m src.run_pipeline
```

### Compute IC seperately
```bash
python -m src.compute_ic
```

## Summary

This project implements a full quantitative equity research pipeline using CRSP and Compustat data. It focuses on constructing fundamental signals, ensuring point-in-time data integrity, and evaluating predictive power through Information Coefficient (IC) analysis across multiple forward return horizons.

The framework reflects real-world quant workflows, including data cleaning, feature engineering, and statistically rigorous evaluation. Results highlight the behavior of value and profitability factors over time, consistent with empirical asset pricing literature.

---

## Author

**Omar Faruque**  
MS in Quantitative Finance  