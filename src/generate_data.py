import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    """
    Fetches daily data to compare S&P 500 vs Trend Following.
    Uses ^GSPC for long history and ^IRX for interest rates.
    """
    # ==========================================
    # 1. CONFIGURATION & SETUP
    # ==========================================
    filename = Path(__file__).parent / "data.csv"
    initial_cash = 10000
    monthly_add = 500
    
    print(f"Fetching historical data for S&P 500 Index and Treasury Rates...")
    
    # ==========================================
    # 2. PRICE DATA ACQUISITION
    # ==========================================
    # Use ^GSPC for data going back decades instead of VOO
    raw_data = yf.download(['^GSPC', '^IRX'], period="max", interval="1d", auto_adjust=True)
    
    # Extract closing prices and drop days where either is missing (alignment)
    closes = raw_data['Close'].dropna()
    
    # ==========================================
    # 3. STRATEGY CALCULATION
    # ==========================================
    sp_pct = closes['^GSPC'].pct_change()
    # Convert annual Treasury yield to daily rate
    daily_cash_rate = (closes['^IRX'] / 100) / 252
    
    # Momentum Signal: 5 red days to exit, 5 green days to enter
    day_direction = np.sign(sp_pct) 
    rolling_sum = day_direction.rolling(window=5).sum()

    invest_monthly_bal = [initial_cash]
    trend_following_bal = [initial_cash]
    
    in_market = True 
    dates = sp_pct.index.tolist()

    # Start loop from the first day we have a valid percent change
    for i in range(1, len(dates)):
        contribution = monthly_add if dates[i].month != dates[i-1].month else 0
        
        # Signal Logic (Check previous day's rolling sum)
        if rolling_sum.iloc[i-1] == -5:
            in_market = False 
        elif rolling_sum.iloc[i-1] == 5:
            in_market = True  

        # --- Calculate Balances ---
        # Invest Monthly: Always S&P 500 returns
        new_monthly = invest_monthly_bal[-1] * (1 + sp_pct.iloc[i]) + contribution
        invest_monthly_bal.append(new_monthly)
        
        # Trend Following: Market return if IN, Treasury rate if OUT
        current_yield = sp_pct.iloc[i] if in_market else daily_cash_rate.iloc[i]
        new_trend = trend_following_bal[-1] * (1 + current_yield) + contribution
        trend_following_bal.append(new_trend)

    # ==========================================
    # 5. CLEANING & EXPORT
    # ==========================================
    res = pd.DataFrame({
        'Date': dates,
        'Passive Invest': invest_monthly_bal,
        'Active Invest': trend_following_bal
    }).dropna()
    
    res['Date'] = pd.to_datetime(res['Date']).dt.strftime('%Y-%m-%d')
    res.to_csv(filename, index=False)
    print(f"Done! Created {filename} starting from {res['Date'].iloc[0]}.")
    return res

if __name__ == "__main__":
    get_portfolio_data()
