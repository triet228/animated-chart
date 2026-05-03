import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    """
    Generates 40-year US Treasury Bond trajectories.
    Each starting year (1960-1985) tracks a $10,000 investment.
    """
    filename = Path(__file__).parent / "data.csv"
    initial_investment = 10000
    duration = 40
    
    # Historical Annual Total Returns for 10-Year US Treasury Bonds (1960-2024)
    # Source: Aswath Damodaran (NYU Stern) - Includes Coupons & Price appreciation
    bond_returns = {
        1960: 11.64, 1961: 2.06, 1962: 5.69, 1963: 1.68, 1964: 3.73, 1965: 0.72,
        1966: 2.91, 1967: -1.58, 1968: 3.27, 1969: -5.01, 1970: 16.75, 1971: 9.79,
        1972: 2.82, 1973: 3.66, 1974: 1.99, 1975: 3.61, 1976: 15.98, 1977: 1.29,
        1978: -0.78, 1979: 0.67, 1980: -2.99, 1981: 8.20, 1982: 32.81, 1983: 3.20,
        1984: 13.73, 1985: 25.71, 1986: 24.28, 1987: -4.96, 1988: 8.22, 1989: 17.69,
        1990: 6.24, 1991: 15.00, 1992: 9.36, 1993: 14.21, 1994: -8.04, 1995: 23.48,
        1996: 1.43, 1997: 9.94, 1998: 14.92, 1999: -8.25, 2000: 16.66, 2001: 5.57,
        2002: 15.12, 2003: 0.38, 2004: 4.49, 2005: 2.87, 2006: 1.97, 2007: 10.21,
        2008: 20.10, 2009: -11.12, 2010: 8.46, 2011: 16.04, 2012: 2.97, 2013: -9.10,
        2014: 10.75, 2015: 1.28, 2016: 0.69, 2017: 2.80, 2018: -0.02, 2019: 9.64,
        2020: 11.33, 2021: -3.65, 2022: -17.83, 2023: 4.49, 2024: 3.50, 2025: 4.00
    }

    dates = pd.date_range(start="1900-01-01", periods=duration + 1, freq='YS')
    res = pd.DataFrame({'Date': dates})

    # Simulate $10k compounding for each starting year from 1960 to 1985
    for start_year in range(1960, 1986):
        path = [initial_investment]
        current_val = initial_investment
        for offset in range(1, duration + 1):
            year_ret = bond_returns.get(start_year + offset - 1, 4.0) / 100
            current_val *= (1 + year_ret)
            path.append(current_val)
        res[f'Start {start_year}'] = path

    # Comparison bounds
    years_held = np.arange(duration + 1)
    res['8.5%'] = initial_investment * (1.085 ** years_held)
    res['5.5%'] = initial_investment * (1.055 ** years_held)

    res.to_csv(filename, index=False)
    return res

if __name__ == "__main__":
    get_portfolio_data()
