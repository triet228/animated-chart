# src/generate_data.py

import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import datetime
from pathlib import Path


filename = Path(__file__).parent / "data.csv"

# ETFs used to simulate the portfolios
etf_tickers = ['VOO', 'VUG', 'VB', 'VXUS', 'VTI', 'BND']

print(f"Fetching max historical data for: {etf_tickers}")

# 2. Download Real Monthly Data
df_raw = yf.download(etf_tickers, period="max", interval="1mo", auto_adjust=True)

if 'Close' in df_raw.columns:
    prices = df_raw['Close']
else:
    prices = df_raw

# 3. Calculate Monthly Percentage Change
# pct_change() returns a decimal, keep it for math, then multiply by 100 later
monthly_returns = prices.pct_change() 

# Calculate the Portfolios
# Dave Ramsey: Equal weight (25%) across 4 funds
ramsey_returns = (
    monthly_returns['VOO'] * 0.25 + 
    monthly_returns['VUG'] * 0.25 + 
    monthly_returns['VB'] * 0.25 + 
    monthly_returns['VXUS'] * 0.25
)

# Boglehead: 60% US, 20% Int'l, 20% Bonds
boglehead_returns = (
    monthly_returns['VTI'] * 0.60 + 
    monthly_returns['VXUS'] * 0.20 + 
    monthly_returns['BND'] * 0.20
)

# Create a new DataFrame for our target returns
returns = pd.DataFrame({
    'Dave Ramsey': ramsey_returns * 100,
    'Boglehead': boglehead_returns * 100
})

# --- Fetch Inflation Data (CPI) from FRED ---
print("Fetching inflation data from FRED...")
start_date = returns.index.min()
end_date = datetime.date.today()
try:
    cpi_data = web.DataReader('CPIAUCSL', 'fred', start_date, end_date)
    cpi_returns = cpi_data.pct_change() * 100
    cpi_returns.columns = ['Inflation']
    returns.index = returns.index.tz_localize(None) 
    returns = returns.join(cpi_returns)
except Exception as e:
    print(f"Could not fetch FRED data: {e}")

# 4. Clean and Rename
df = returns.dropna(subset=['Dave Ramsey', 'Boglehead']).reset_index()
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# 5. Format as Percentage Strings
cols_to_format = ['Dave Ramsey', 'Boglehead', 'Inflation']
for col in cols_to_format:
    if col in df.columns:
        df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

# 6. Save
df.to_csv(filename, index=False)
print(f"Done! Created {filename} with columns: {df.columns.tolist()}")
