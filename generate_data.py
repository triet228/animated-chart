import yfinance as yf
import pandas as pd

# 1. Configuration
filename = "data.csv"

# Define your base indices and the exact leverage multipliers you want.
# 1 = standard (no leverage). You can add 3, 4, 5, or even 10!
LEVERAGE_CONFIG = {
    'SP500': {'ticker': '^GSPC', 'leverages': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
}

print("Fetching max historical DAILY data to simulate accurate leverage...")

# Extract raw tickers to download
raw_tickers = [info['ticker'] for info in LEVERAGE_CONFIG.values()]

# 2. Download Real Daily Data 
# (Daily data is REQUIRED to accurately simulate how leveraged funds compound)
df_raw = yf.download(raw_tickers, period="max", interval="1d", auto_adjust=True)

if 'Close' in df_raw.columns:
    prices = df_raw['Close']
else:
    prices = df_raw

# 3. Calculate Daily Returns
daily_returns = prices.pct_change()

# 4. Simulate Leveraged Daily Returns and Convert to Price Index
simulated_daily_prices = pd.DataFrame(index=daily_returns.index)

for clean_name, config in LEVERAGE_CONFIG.items():
    ticker = config['ticker']
    base_daily_returns = daily_returns[ticker]
    
    for lev in config['leverages']:
        col_name = f"{clean_name}" if lev == 1 else f"{lev}x"
        
        # Multiply daily returns by the leverage factor
        lev_daily_returns = base_daily_returns * lev
        
        # Create a cumulative price index (starting at 100)
        # cumprod() simulates the daily compounding of a leveraged ETF
        simulated_daily_prices[col_name] = (1 + lev_daily_returns).cumprod() * 100

# 5. Resample to Monthly and Calculate Monthly Returns
# 'ME' groups the daily data by Month End
monthly_prices = simulated_daily_prices.resample('ME').last()
monthly_returns = monthly_prices.pct_change() * 100

# 6. Clean and Format
df = monthly_returns.dropna(how='all').reset_index()
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

# Format as Percentage Strings to match your old output exactly
cols_to_format = [col for col in df.columns if col != 'Date']
for col in cols_to_format:
    df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

# 7. Save
df.to_csv(filename, index=False)
print(f"Done! Created {filename} with columns: {cols_to_format}")
