import yfinance as yf
import pandas as pd

filename = "data.csv"
INITIAL_BALANCE = 1
SP500_WEIGHT = 1.00
CASH_WEIGHT = 0.00
CASH_ANNUAL_INTEREST = 0.03
ANNUAL_INFLATION = 0.025
CONTRIBUTIONS = [100, 500, 1000] 

# 1. Market Growth (Real Terms)
df_raw = yf.download("^GSPC", period="max", interval="1d", auto_adjust=True)
prices = df_raw['Close']
if isinstance(prices, pd.DataFrame): prices = prices.iloc[:, 0]

sp500_ret = prices.pct_change().dropna()
daily_cash = (1 + CASH_ANNUAL_INTEREST)**(1/252) - 1
daily_inf = (1 + ANNUAL_INFLATION)**(1/252) - 1
# Real Daily Return = ((1 + Nominal) / (1 + Inflation)) - 1
nominal_daily = (sp500_ret * SP500_WEIGHT) + (daily_cash * CASH_WEIGHT)
daily_real_return = ((1 + nominal_daily) / (1 + daily_inf)) - 1
monthly_market_growth = (1 + daily_real_return).resample('ME').prod()

# 2. Simulate Dollar Balances
df_final = pd.DataFrame(index=monthly_market_growth.index)
monthly_inf_factor = (1 + ANNUAL_INFLATION)**(1/12)

for amount in CONTRIBUTIONS:
    balance = INITIAL_BALANCE
    current_adj_contribution = amount
    balance_history = []
    
    for market_growth in monthly_market_growth:
        # Market acts on existing money, then we add the new money
        balance = (balance * market_growth) + current_adj_contribution
        balance_history.append(balance)
        
        # Increase contribution for next month to keep up with inflation
        current_adj_contribution *= monthly_inf_factor
        
    df_final[str(amount)] = balance_history

# 3. Export
df_final.index.name = 'Date'
df_final.to_csv(filename)
print(f"Done! {filename} now contains actual dollar balances.")
