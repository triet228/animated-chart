import yfinance as yf
import pandas as pd

# 1. Configuration
filename = "data.csv"
# Mapping dictionary to rename symbols to clean names later
ticker_map = {
    '^GSPC': 'SP500',
    '^IXIC': 'NASDAQ',
    'VOO': 'VOO',
    'ONEQ': 'ONEQ',
    'AAPL': 'AAPL',
    'TSLA': 'TSLA',
    'GC=F': 'Gold',
}

tickers = list(ticker_map.keys())

print(f"Fetching max historical data for: {tickers}")

# 2. Download Real Monthly Data
# 'auto_adjust=True' makes 'Close' the same as 'Adj Close'
df_raw = yf.download(tickers, period="max", interval="1mo", auto_adjust=True)

# 3. Extract just the 'Close' prices
# If downloading multiple tickers, 'Close' is a level in the MultiIndex
if 'Close' in df_raw.columns:
    prices = df_raw['Close']
else:
    # Fallback if only one ticker or different structure
    prices = df_raw

# 4. Calculate Monthly Percentage Change
returns = prices.pct_change() * 100

# 5. Clean and Rename
df = returns.dropna(how='all').reset_index()
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Rename columns using our map
df = df.rename(columns=ticker_map)

# 6. Format as Percentage Strings
# We use the values from the map for the loop
for col in ticker_map.values():
    if col in df.columns:
        df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

# 7. Save
df.to_csv(filename, index=False)
print(f"Done! Created {filename} with cleaned columns: {list(ticker_map.values())}")
