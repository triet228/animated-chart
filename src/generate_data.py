import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import datetime
from pathlib import Path

def get_portfolio_data():
    """
    Fetches historical ETF data, calculates portfolio returns, 
    and merges with inflation data from FRED.
    """
    # ==========================================
    # 1. CONFIGURATION & SETUP
    # ==========================================
    filename = Path(__file__).parent / "data.csv"
    etf_tickers = ['VOO', 'VUG', 'VB', 'VXUS', 'VTI', 'BND']
    
    print(f"Fetching max historical data for: {etf_tickers}")
    
    # ==========================================
    # 2. PRICE DATA ACQUISITION
    # ==========================================
    df_raw = yf.download(etf_tickers, period="max", interval="1mo", auto_adjust=True)
    
    # Extract closing prices
    prices = df_raw['Close'] if 'Close' in df_raw.columns else df_raw
    
    # Calculate Monthly Percentage Change
    monthly_returns = prices.pct_change() 
    
    # ==========================================
    # 3. PORTFOLIO CALCULATION
    # ==========================================
    # Dave Ramsey: 25% Growth, 25% Growth & Income, 25% Aggressive, 25% International
    ramsey_returns = (
        monthly_returns['VOO'] * 0.25 + 
        monthly_returns['VUG'] * 0.25 + 
        monthly_returns['VB'] * 0.25 + 
        monthly_returns['VXUS'] * 0.25
    )
    
    # Boglehead Three-Fund: 60% Total US, 20% Total Int'l, 20% Total Bonds
    boglehead_returns = (
        monthly_returns['VTI'] * 0.60 + 
        monthly_returns['VXUS'] * 0.20 + 
        monthly_returns['BND'] * 0.20
    )
    
    # Create the primary DataFrame (values as percentages)
    returns = pd.DataFrame({
        'Dave Ramsey': ramsey_returns * 100,
        'Boglehead': boglehead_returns * 100
    })
    
    # ==========================================
    # 4. EXTERNAL DATA (FRED INFLATION)
    # ==========================================
    print("Fetching inflation data from FRED...")
    start_date = returns.index.min()
    end_date = datetime.date.today()
    
    try:
        cpi_data = web.DataReader('CPIAUCSL', 'fred', start_date, end_date)
        cpi_returns = cpi_data.pct_change() * 100
        cpi_returns.columns = ['Inflation']
        
        # Align timezones and join datasets
        returns.index = returns.index.tz_localize(None) 
        returns = returns.join(cpi_returns)
    except Exception as e:
        print(f"Could not fetch FRED data: {e}")
    
    # ==========================================
    # 5. CLEANING & EXPORT
    # ==========================================
    # Filter for rows where both main portfolios have data
    df = returns.dropna(subset=['Dave Ramsey', 'Boglehead']).reset_index()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    # Convert numerical values to formatted strings for CSV
    cols_to_format = ['Dave Ramsey', 'Boglehead', 'Inflation']
    for col in cols_to_format:
        if col in df.columns:
            df[col] = df[col].map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
    
    df.to_csv(filename, index=False)
    print(f"Done! Created {filename} with columns: {df.columns.tolist()}")
    
    return df

if __name__ == "__main__":
    get_portfolio_data()
