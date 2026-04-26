import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import datetime

# 1. Configuration
filename = "data.csv"
ticker_map = {
    '^GSPC': 'SP500',
    '^IXIC': 'NASDAQ',
    'VOO': 'VOO',
    'ONEQ': 'ONEQ',
    'AAPL': 'AAPL',
    'TSLA': 'TSLA',
    'GC=F': 'Gold',
    'XLE': 'Energy',
    'XLV': 'HealthCare',
    'BTC-USD': 'Bitcoin',
    'VNQ': 'Real Estate',
    '005930.KS': 'Samsung',
    'ZM': 'Zoom',
}

tickers = list(ticker_map.keys())

print(f"Fetching max historical data for: {tickers}")

# 2. Download Real Monthly Data
df_raw = yf.download(tickers, period="max", interval="1mo", auto_adjust=True)

if 'Close' in df_raw.columns:
    prices = df_raw['Close']
else:
    prices = df_raw

# 3. Calculate Monthly Percentage Change
returns = prices.pct_change() * 100

# --- Fetch Inflation Data (CPI) from FRED ---
print("Fetching inflation data from FRED...")
start_date = returns.index.min()
end_date = datetime.date.today()
cpi_data = web.DataReader('CPIAUCSL', 'fred', start_date, end_date)

# Calculate monthly inflation rate
cpi_returns = cpi_data.pct_change() * 100
cpi_returns.columns = ['Inflation']

# Remove timezone from yfinance index so it can merge with FRED data
returns.index = returns.index.tz_localize(None) 
returns = returns.join(cpi_returns)

# --- NEW: Add 10% Annual Constant Return ---
# Convert 10% annual to a monthly compounded rate
monthly_10_percent = ((1.09 ** (1/12)) - 1) * 100
returns['9% Annual'] = monthly_10_percent
# ------------------------------------------

# 4. Clean and Rename
df = returns.dropna(how='all').reset_index()
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

df = df.rename(columns=ticker_map)

# 5. Format as Percentage Strings
cols_to_format = list(ticker_map.values()) + ['Inflation', '7% Annual']
for col in cols_to_format:
    if col in df.columns:
        df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

# 6. Save
df.to_csv(filename, index=False)
print(f"Done! Created {filename} with cleaned columns: {cols_to_format}")
