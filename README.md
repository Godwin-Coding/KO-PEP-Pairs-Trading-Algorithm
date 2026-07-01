# KO/PEP Pairs Trading Algorithm

A statistical arbitrage project exploring whether Coca-Cola (KO) and PepsiCo (PEP) stock prices share a stable, mean-reverting relationship that can be exploited via a cointegration-based pairs trading strategy.

This project was built as a self-directed learning exercise to understand the full pipeline of quantitative pairs trading — from data sourcing and statistical validation, to strategy construction and honest backtesting.

## Summary of Results

| Metric | Value |
|---|---|
| Cointegration p-value (Engle-Granger) | 0.0095 |
| Hedge ratio (OLS) | 3.3157 |
| Sharpe Ratio | 0.11 |
| Max Drawdown | -66.7% |
| CAGR | 2.74% |

**Key finding:** despite KO and PEP being statistically cointegrated (p = 0.0095), the resulting strategy underperformed simply holding cash (risk-free rate ~4-5%) and carried a severe drawdown during the 2020 COVID crash. This is a deliberately honest result — the full writeup explains why, including the likelihood of **alpha decay** on a heavily-arbitraged, textbook pair, and several concrete methodological limitations.

## Hypothesis

KO and PEP sell similar products to similar consumers, face similar input costs, and are valued using similar multiples — so their prices may share a stable, proportional long-run relationship that occasionally diverges and reverts. This project tests that hypothesis rigorously rather than assuming it.

## Methodology

1. **Data sourcing** — 9 years (2015–2024) of daily closing prices via `yfinance`
2. **Data cleaning** — missing value handling, minimum history requirement, date synchronisation checks, outlier detection with manual investigation of flagged dates, and a stationarity sanity check (ADF test) on returns
3. **Cointegration testing** — Engle-Granger test to confirm a statistically valid long-run equilibrium relationship
4. **Hedge ratio estimation** — OLS regression to determine the dollar-neutral weighting between the two stocks
5. **Spread construction** — computing and visualising the regression residuals (the tradeable spread)
6. **Signal generation** — rolling z-score of the spread, with entry/exit thresholds
7. **Backtesting** — lookahead-bias-free simulation using lagged positions against realised returns
8. **Performance evaluation** — Sharpe ratio, max drawdown, CAGR
9. **Critical reflection** — explicit documentation of limitations and concrete improvements

## Key Limitations (detailed in notebook)

- Static hedge ratio across the full 9-year window, despite a clear post-2020 volatility regime shift
- Engle-Granger's directional asymmetry (PEP-on-KO vs. KO-on-PEP) not fully resolved via the Johansen test
- Flat risk-free rate approximation rather than historical T-bill rates
- No transaction cost, slippage, or borrowing cost modelling
- Fixed, unoptimised entry/exit thresholds (no walk-forward validation)
- Single pair only — no diversification across a basket of cointegrated pairs
- No volatility-adjusted position sizing or stop-loss mechanism

Each of these is discussed in depth in the notebook, along with a concrete proposed implementation for addressing it.

## Tech Stack

- `yfinance` — data sourcing
- `pandas` / `numpy` — data manipulation
- `statsmodels` — ADF test, Engle-Granger cointegration test, OLS regression
- `matplotlib` — visualisation

## Repository Structure

```
├── main.ipynb      # Full annotated notebook: methodology, code, and analysis
├── no_notes.py     # Clean implementation without annotations, for quick reference
├── README.md
└── LICENSE
```

## Running This Project

**Annotated notebook** (recommended — includes full methodology and explanation):
```bash
pip install yfinance pandas numpy statsmodels matplotlib pandas-datareader
jupyter notebook main.ipynb
```

**Clean script** (code only, no annotations):
```bash
pip install yfinance pandas numpy statsmodels matplotlib pandas-datareader
python no_notes.py
```

## References

- Engle, R. F., & Granger, C. W. J. (1987). *Co-integration and Error Correction: Representation, Estimation, and Testing.* Econometrica.
- Vidyamurthy, G. (2004). *Pairs Trading: Quantitative Methods and Analysis.* Wiley.

## License & Usage

This project is shared publicly for portfolio and educational purposes. See [LICENSE](./LICENSE) for usage terms. If you reference or build on this work, please credit the original author.

---

*Built by Godwin as an independent learning project to understand statistical arbitrage and cointegration-based trading strategies.*
