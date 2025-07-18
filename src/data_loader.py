import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf

def fetch_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Downloads Close prices for the given ticker and date range.
    Tries Stooq first, then yfinance as fallback.
    Forward-fills missing data, sets Date as index, and returns a DataFrame with a 'Close' column.
    Prints/logs which data source was used.
    Raises ValueError if ticker is invalid or no data is returned.
    """
    # Try Stooq first
    try:
        df = pdr.get_data_stooq(ticker, start=start, end=end)
        if not df.empty:
            print(f"Fetched data for {ticker} from Stooq.")
            df = df[['Close']]
            df = df.ffill()
            df.index.name = 'Date'
            df = df.sort_index() # stooq returns data in descending order
            return df
        else:
            print(f"Stooq returned empty data for {ticker}.")
    except Exception as e:
        print(f"Stooq failed for {ticker}: {e}")
    # Fallback to yfinance
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            raise ValueError(f"No data found for ticker '{ticker}' in the given date range from yfinance.")
        # Handle multi-index columns (new yfinance default)
        if isinstance(data.columns, pd.MultiIndex):
            if ('Close', ticker) in data.columns:
                close = data[('Close', ticker)]
            else:
                raise ValueError(f"'Close' column not found for ticker '{ticker}' in yfinance data.")
        else:
            if 'Close' in data.columns:
                close = data['Close']
            else:
                raise ValueError(f"'Close' column not found in yfinance data.")
        df = pd.DataFrame({'Close': close}).ffill()
        df.index.name = 'Date'
        print(f"Fetched data for {ticker} from yfinance.")
        return df
    except Exception as e:
        print(f"yfinance failed for {ticker}: {e}")
    raise ValueError(f"Failed to fetch data for ticker '{ticker}' from all available sources.")