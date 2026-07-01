'''This file was created to view the full code without the long paragraphs of notes'''

import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, coint
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
import matplotlib.pyplot as plt


# Step 1: Data Retrieval
tickers = ["KO", "PEP"]
START, END = "2015-01-01", "2024-01-01"
df = yf.download(tickers, start=START, end=END) #returns a pandas dataframe object 
prices = df["Close"]





# Step 2: Data Cleaning 

#2A Filtering NaN values with .ffill() and .dropna()
prices = prices.ffill()
prices = prices.dropna()

#2B Minimum History Requirement 
MIN_YEARS = 5
assert len(prices) >= 252 * MIN_YEARS, f"Need at least {MIN_YEARS} years of data"

# will produce 
# AssertionError: Need at least __ years of data
# if not enough data

#2C Synchronisation Test
#Note .equals is a pandas function, but yfinance imports it internally and the Dataframe it returns is a panddas object
assert prices["KO"].index.equals(prices["PEP"].index), "Tickers have misaligned trading dates"

#2D Outlier Check
returns = prices.pct_change() #converting each data in the table to percentage change
mean = returns.mean() #returning a 1rx2c Series. Contains the means of KO and PEP from the percentage change data
std = returns.std() #returning a 1rx2c Series. Contains the standard deviations (σ) of KO and PEP from the percentage change data
mask = (returns - mean).abs() > 5 * std 
print("-" * 10, "Step 2D: Outlier Check", "-" * 10)
print(mask.sum())

ko_outliers = returns["KO"][mask["KO"]]
pep_outliers = returns["PEP"][mask["PEP"]]

print("KO outliers:")
print(ko_outliers)
print("\nPEP outliers:")
print(pep_outliers)

#2E Stationary Check
print("\n\n\n", "-" * 10, "Step 2E: Stationary Check", "-" * 10)
for ticker in ["KO", "PEP"]:
    result = adfuller(prices[ticker].pct_change().dropna())
    print(f"{ticker} ADF p-value: {result[1]:.4f}")





#Step 3: Engle-Granger Cointegration Test
print("\n\n\n", "-" * 10, "Step 3: Engle-Granger Cointegration Test", "-" * 10)
score, pvalue, critical_values = coint(prices["KO"], prices["PEP"])
print(f"test score: {score:.4f}")
print(f"p-value: {pvalue:.4f}")
print(f"Critical values: {critical_values}")





#Step 4: OLS Regression to Estimate Hedge Ratio
print("\n\n\n", "-" * 10, "Step 4: OLS Regression to Estimate Hedge Ratio", "-" * 10)
X = add_constant(prices["KO"])
model = OLS(prices["PEP"], X)
model = model.fit()
print(model.summary())
hedge_ratio = model.params["KO"]
print(f"\nHedge ratio: {hedge_ratio:.4f}")





#Step 5: Computing & Visualising the Dollar-Neutral Spread
spread = model.resid #returns a Series

## OR
# alpha = model.params["const"]
# spread = prices["PEP"] - alpha - hedge_ratio * prices["KO"]
print("\n\n\n", "-" * 10, "Step 5: Computing & Visualising the Dollar-Neutral Spread", "-" * 10)
print("Graph generated")
spread.plot(title="KO/PEP Spread (Residuals)")
plt.axhline(spread.mean(), color="red", linestyle="--", label="Mean")
plt.legend() #shows us the legends of the graph (the mean box in the top right showing what the red horizontal line means)
plt.show() #actually displays the graph





#Step 6: Z-Score and Signal Generation
def zscore(series, window=30):
    mean_spread_window = series.rolling(window).mean() # mean raw spread value of last 30 days, computed for each day
    std_spread_window = series.rolling(window).std() # std of the raw spread value of last 30 days, computed for each day
    return (series - mean_spread_window) / std_spread_window # return a series containing z-scores for the raw spread value of each day, using mean and std spread values from the last 30 days, starting from the current day 

print("\n\n\n", "-" * 10, "Step 6: Z-Score and Signal Generation", "-" * 10)
print("Graph Generated")
z = zscore(spread) #calling the zscore function on the spread series, returning a series 
z.plot(title="Z-Score of Spread")
plt.axhline(2.0, color="red", linestyle="--", label="Short signal")
plt.axhline(-2.0, color="green", linestyle="--", label="Long signal")
plt.axhline(0, color="black", linestyle="-", label="Mean")
plt.legend()
plt.show()






#Step 7a: Backtesting using Cumulative Returns Chart
# Generate signals
long_entry  = z < -2.0 #generating a boolean Series based on whether each zscore value for that day fulfills the condition 
short_entry = z > 2.0 
exit_signal = abs(z) < 0.5

# Build positions
positions = pd.DataFrame(index=prices.index, columns=["PEP", "KO"]).fillna(0.0)

for i in range(1, len(z)):
    if pd.isna(z.iloc[i]):
        positions.iloc[i] = [0, 0]
    elif long_entry.iloc[i]:
        positions.iloc[i] = [1, -hedge_ratio]
    elif short_entry.iloc[i]:
        positions.iloc[i] = [-1, hedge_ratio]
    elif exit_signal.iloc[i]:
        positions.iloc[i] = [0, 0]
    else:
        positions.iloc[i] = positions.iloc[i-1] #same position, just copy the previous day's action

# Calculate P&L
returns = prices.pct_change() #redeclared again for visual convenience
pnl = (positions.shift(1) * returns).sum(axis=1) #Individual P&L per day in the form of percentage returns
cumulative = (1 + pnl).cumprod() #Cumulative P&L overtime after each day of trading using compounding 

print("\n\n\n", "-" * 10, "Step 7a: Backtesting using Cumulative Returns Chart", "-" * 10)
print("Graph generated")
cumulative.plot(title="Cumulative Returns")
plt.axhline(1.0, color="red", linestyle="--")
plt.show()






#Step 7b: Backtesting using Sharpe Ratio, Max Drawdown and CAGR
# Sharpe Ratio (annualised)
trading_days = 252
risk_free_rate = 0.0397  # approximate current US T-bill rate, annualised
daily_rf = risk_free_rate / trading_days #very rough estimate of daily risk free rate
daily_sharpe = (pnl - daily_rf).mean() / pnl.std()
annual_sharpe = daily_sharpe * np.sqrt(trading_days) 

# Max Drawdown
rolling_max = cumulative.cummax()
drawdown = (rolling_max - cumulative) / rolling_max
max_drawdown = drawdown.max()

# CAGR (Compound Annual Growth Rate)
n_years = len(pnl) / trading_days
cagr = cumulative.iloc[-1] ** (1 / n_years) - 1

print("\n\n\n", "-" * 10, "Step 7b: Backtesting using Sharpe Ratio, Max Drawdown and CAGR", "-" * 10)
print(f"Sharpe Ratio: {annual_sharpe:.4f}")
print(f"Max Drawdown: {max_drawdown:.4f}")
print(f"CAGR: {cagr:.4f}")