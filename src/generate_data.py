import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    """
    Generates realistic 40-year gold trajectories starting at different years.
    Each starting year is treated as its own portfolio.
    """
    filename = Path(__file__).parent / "data.csv"
    initial_investment = 10000
    duration = 40
    
    # Historical Annual Average Gold Prices (1973 - 2025)
    gold_prices = {
        1973: 97.12, 1974: 158.76, 1975: 160.87, 1976: 124.80, 1977: 147.84,
        1978: 193.57, 1979: 307.01, 1980: 614.75, 1981: 459.16, 1982: 376.11,
        1983: 423.71, 1984: 360.65, 1985: 317.42, 1986: 368.20, 1987: 446.84,
        1988: 436.78, 1989: 381.27, 1990: 383.73, 1991: 362.34, 1992: 343.87,
        1993: 360.05, 1994: 384.16, 1995: 384.07, 1996: 387.73, 1997: 331.00,
        1998: 294.12, 1999: 278.86, 2000: 279.29, 2001: 271.19, 2002: 310.08,
        2003: 363.83, 2004: 409.53, 2005: 444.99, 2006: 604.34, 2007: 696.43,
        2008: 872.37, 2009: 973.66, 2010: 1226.66, 2011: 1573.16, 2012: 1668.86,
        2013: 1409.51, 2014: 1266.06, 2015: 1158.86, 2016: 1251.92, 2017: 1260.39,
        2018: 1268.93, 2019: 1393.34, 2020: 1773.73, 2021: 1798.89, 2022: 1801.87,
        2023: 1927.99, 2024: 2380.00, 2025: 3000.00
    }

    # Prepare DataFrame with dummy dates (Year 0 to 40)
    dates = pd.date_range(start="1900-01-01", periods=duration + 1, freq='YS')
    res = pd.DataFrame({'Date': dates})

    # Add realistic trajectories for each starting year from 1973 to 1985
    for start_year in range(1973, 1986):
        base_price = gold_prices[start_year]
        path = []
        for offset in range(duration + 1):
            current_val = (gold_prices[start_year + offset] / base_price) * initial_investment
            path.append(current_val)
        res[f'Start {start_year}'] = path

    # Add theoretical return bounds
    years_held = np.arange(duration + 1)
    res['8%'] = initial_investment * (1.08 ** years_held)
    res['2%'] = initial_investment * (1.02 ** years_held)

    res.to_csv(filename, index=False)
    print(f"Realistic data created: {filename}")
    return res

if __name__ == "__main__":
    get_portfolio_data()
