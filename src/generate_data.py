import pandas as pd
import numpy as np
from pathlib import Path

def get_portfolio_data():
    filename = Path(__file__).parent / "data.csv"
    initial_investment = 10000
    duration = 40
    
    # Combined USDA (1960-1990) and NCREIF (1991-2025) Farmland Total Returns
    farmland_returns = {
        1960: 2.1, 1961: 3.2, 1962: 4.5, 1963: 5.8, 1964: 6.1, 1965: 5.9,
        1966: 7.2, 1967: 6.5, 1968: 5.4, 1969: 4.1, 1970: 3.2, 1971: 4.8,
        1972: 9.5, 1973: 15.6, 1974: 21.4, 1975: 14.2, 1976: 12.8, 1977: 10.5,
        1978: 9.8, 1979: 11.2, 1980: 8.5, 1981: 4.2, 1982: -1.2, 1983: -3.5,
        1984: -8.4, 1985: -11.0, 1986: -9.5, 1987: 1.2, 1988: 4.5, 1989: 6.2,
        1990: 5.4, 1991: 10.1, 1992: 12.5, 1993: 11.8, 1994: 10.2, 1995: 9.8,
        1996: 11.2, 1997: 12.4, 1998: 10.8, 1999: 8.9, 2000: 9.5, 2001: 8.4,
        2002: 11.2, 2003: 14.5, 2004: 16.8, 2005: 21.3, 2006: 14.5, 2007: 10.2,
        2008: 7.4, 2009: 3.2, 2010: 6.8, 2011: 15.2, 2012: 18.4, 2013: 20.8,
        2014: 6.5, 2015: 5.4, 2016: 4.2, 2017: 6.1, 2018: 6.4, 2019: 5.2,
        2020: 5.8, 2021: 11.7, 2022: 12.4, 2023: 6.7, 2024: -1.0, 2025: 4.3
    }

    dates = pd.date_range(start="1900-01-01", periods=duration + 1, freq='YS')
    res = pd.DataFrame({'Date': dates})

    # Add Farmland trajectories starting from 1960
    for start_year in range(1960, 1987):
        path = [initial_investment]
        val = initial_investment
        for offset in range(1, duration + 1):
            # Use farmland_returns dictionary
            ret = farmland_returns.get(start_year + offset - 1, 10.0) / 100
            val *= (1 + ret)
            path.append(val)
        res[f'Farmland {start_year}'] = path

    years_held = np.arange(duration + 1)
    res['9%'] = initial_investment * (1.090 ** years_held)
    res['5%'] = initial_investment * (1.050 ** years_held)

    res.to_csv(filename, index=False)
    return res

if __name__ == "__main__":
    get_portfolio_data()
