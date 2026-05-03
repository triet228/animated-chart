import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    filename = Path(__file__).parent / "data.csv"
    initial_investment = 10000
    duration = 40
    
    # Silver Historical Annual Returns (1969-2024)
    silver_returns = {
        1969: -8.2, 1970: -8.9, 1971: -16.0, 1972: 48.2, 1973: 60.6, 1974: 37.1,
        1975: -6.5, 1976: 4.3, 1977: 9.2, 1978: 26.5, 1979: 434.9, 1980: -51.9,
        1981: -47.4, 1982: 33.4, 1983: -18.0, 1984: -29.4, 1985: -7.8, 1986: -9.0,
        1987: 26.9, 1988: -9.7, 1989: -13.7, 1990: -19.7, 1991: -7.9, 1992: -4.9,
        1993: 39.5, 1994: -5.3, 1995: 6.0, 1996: -6.6, 1997: 25.0, 1998: -16.5,
        1999: 6.4, 2000: -14.1, 2001: -1.3, 2002: 3.3, 2003: 27.8, 2004: 14.2,
        2005: 29.5, 2006: 46.1, 2007: 14.4, 2008: -26.9, 2009: 57.5, 2010: 80.3,
        2011: -8.0, 2012: 6.3, 2013: -34.9, 2014: -18.1, 2015: -13.6, 2016: 15.9,
        2017: 7.1, 2018: -9.4, 2019: 15.4, 2020: 47.4, 2021: -11.6, 2022: 2.6,
        2023: -2.5, 2024: 22.3
    }

    dates = pd.date_range(start="1900-01-01", periods=duration + 1, freq='YS')
    res = pd.DataFrame({'Date': dates})

    # Generate trajectories starting from 1969 to 1985
    for start_year in range(1969, 1986):
        path = [initial_investment]
        val = initial_investment
        for offset in range(1, duration + 1):
            ret = silver_returns.get(start_year + offset - 1, 6.0) / 100
            val *= (1 + ret)
            path.append(val)
        res[f'Silver {start_year}'] = path

    years_held = np.arange(duration + 1)
    res['9%'] = initial_investment * (1.090 ** years_held)
    res['1%'] = initial_investment * (1.010 ** years_held)

    res.to_csv(filename, index=False)
    return res

if __name__ == "__main__":
    get_portfolio_data()
