import yfinance as yf
import pandas as pd
import numpy as np

# 1. Configuration
filename = "data.csv"
SP500_WEIGHT = 0.70
CASH_WEIGHT = 0.30
CASH_ANNUAL_INTEREST = 0.03
ANNUAL_INFLATION = 0.025  # 2.5% average inflation
# Withdrawal rates from 0% to 10%
WITHDRAW_RATES = [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10] 

print(f"Simulating portfolio with {ANNUAL_INFLATION*100}% inflation adjustment...")

# 2. Download S&P 500 Daily Data
df_raw = yf.download("^GSPC", period="max", interval="1d", auto_adjust=True)
prices = df_raw['Close']
sp500_daily_returns = prices.pct_change().dropna()

# 3. Calculate Daily Rates (using 252 trading days)
daily_cash_return = (1 + CASH_ANNUAL_INTEREST)**(1/252) - 1
daily_inflation = ANNUAL_INFLATION / 252

# 4. Simulate Portfolio with Withdrawals & Inflation
simulated_daily_prices = pd.DataFrame(index=sp500_daily_returns.index)

# Base portfolio daily return (70/30 split)
base_port_returns = (sp500_daily_returns * SP500_WEIGHT) + (daily_cash_return * CASH_WEIGHT)

for rate in WITHDRAW_RATES:
    col_name = f"{int(rate*100)}%"
    
    # Calculate Real Return: (Nominal Return - Withdrawal Rate - Inflation)
    daily_withdrawal = rate / 252
    net_real_daily_returns = base_port_returns - daily_withdrawal - daily_inflation
    
    # Compound the daily returns into a price index starting at 100
    simulated_daily_prices[col_name] = (1 + net_real_daily_returns).cumprod() * 100

# 5. Resample to Monthly and Calculate Returns
monthly_prices = simulated_daily_prices.resample('ME').last()
monthly_returns = monthly_prices.pct_change() * 100

# 6. Clean and Format
df = monthly_returns.dropna(how='all').reset_index()
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

cols_to_format = [col for col in df.columns if col != 'Date']
for col in cols_to_format:
    df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "0.00%")

# 7. Save
df.to_csv(filename, index=False)
print(f"Done! Created {filename}. 0% return now means you kept pace with inflation.")
