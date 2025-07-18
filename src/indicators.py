import pandas as pd

def compute_sma(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Returns the simple moving average of df['Close'] over the given window.
    """
    if window > len(df):
        raise ValueError("Window size cannot be larger than the DataFrame length.")
    return df['Close'].rolling(window=window, min_periods=1).mean()

# Example usage to add SMAs:
# df['SMA_fast'] = compute_sma(df, 20)
# df['SMA_slow'] = compute_sma(df, 50) 