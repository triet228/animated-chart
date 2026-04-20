import yfinance as yf
import pandas as pd
from datetime import timedelta

filename = "data.csv"
INITIAL_BALANCE = 1_000_000

# 1. Get Market Data
df_raw = yf.download("^GSPC", period="max", interval="1d", auto_adjust=True)
prices = df_raw['Close']
if isinstance(prices, pd.DataFrame): prices = prices.iloc[:, 0]

# 2. Identify the Longest Recovery Window
running_max = prices.cummax()
drawdown_groups = (prices == running_max).cumsum()
durations = prices.groupby(drawdown_groups).apply(lambda x: x.index[-1] - x.index[0])
longest_group_id = durations.idxmax()

# Get the recovery dates
recovery_period = prices.groupby(drawdown_groups).get_group(longest_group_id)
start_date = recovery_period.index[0]
recovery_date = recovery_period.index[-1]

# 3. Add 2 Years to the selection
extended_end_date = recovery_date + timedelta(days=730)
# Slice the original price data using the new extended range
extended_prices = prices.loc[start_date:extended_end_date]

# 4. Simulate the $1M Investment
daily_ret = extended_prices.pct_change().fillna(0)
balance_history = [INITIAL_BALANCE]

for ret in daily_ret[1:]:
    current_balance = balance_history[-1] * (1 + ret)
    balance_history.append(current_balance)

# 5. Export
df_recovery = pd.DataFrame({'SP500': balance_history}, index=extended_prices.index)
df_recovery.to_csv(filename)

print(f"Simulation Start (Peak): {start_date.date()}")
print(f"Recovery Date (Back to Peak): {recovery_date.date()}")
print(f"Extended End Date: {extended_end_date.date()}")
print(f"Final Balance after extension: ${df_recovery['SP500'].iloc[-1]:,.0f}")
