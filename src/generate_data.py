# src/generate_data.py
import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    filename = Path(__file__).parent / "data.csv"
    initial_investment = 10000
    duration = 40
    
    # Historical Dow Jones Industrial Average (DJIA) Annual Returns (1960-2024)
    djia_returns = {
        1960: -9.3, 1961: 18.7, 1962: -10.8, 1963: 17.0, 1964: 14.6, 1965: 10.9,
        1966: -18.9, 1967: 15.2, 1968: 4.3, 1969: -15.2, 1970: 4.8, 1971: 6.1,
        1972: 14.6, 1973: -16.6, 1974: -27.6, 1975: 38.3, 1976: 17.9, 1977: -17.3,
        1978: -3.1, 1979: 4.2, 1980: 14.9, 1981: -9.2, 1982: 19.6, 1983: 20.3,
        1984: -3.7, 1985: 27.7, 1986: 22.6, 1987: 2.3, 1988: 11.8, 1989: 27.0,
        1990: -4.3, 1991: 20.3, 1992: 4.2, 1993: 13.7, 1994: 2.1, 1995: 33.5,
        1996: 26.0, 1997: 22.6, 1998: 16.1, 1999: 25.2, 2000: -6.2, 2001: -7.1,
        2002: -16.8, 2003: 25.3, 2004: 3.1, 2005: -0.6, 2006: 16.3, 2007: 6.4,
        2008: -33.8, 2009: 18.8, 2010: 11.0, 2011: 5.5, 2012: 7.3, 2013: 26.5,
        2014: 7.5, 2015: -2.2, 2016: 13.4, 2017: 25.1, 2018: -5.6, 2019: 22.3,
        2020: 7.2, 2021: 18.7, 2022: -8.8, 2023: 13.7, 2024: 12.9
    }

    dates = pd.date_range(start="1900-01-01", periods=duration + 1, freq='YS')
    res = pd.DataFrame({'Date': dates})

    # Add Dow Jones trajectories starting from various years
    for start_year in range(1960, 1986):
        path = [initial_investment]
        val = initial_investment
        for offset in range(1, duration + 1):
            ret = djia_returns.get(start_year + offset - 1, 10.0) / 100
            val *= (1 + ret)
            path.append(val)
        res[f'Dow Jones {start_year}'] = path

    years_held = np.arange(duration + 1)
    res['10%'] = initial_investment * (1.100 ** years_held)
    res['5%'] = initial_investment * (1.050 ** years_held)

    res.to_csv(filename, index=False)
    return res

if __name__ == "__main__":
    get_portfolio_data()
