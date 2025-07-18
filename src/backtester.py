import pandas as pd

def backtest_signals(
    df: pd.DataFrame,
    initial_cash: float = 100000,
    transaction_cost: float = 0.001
) -> pd.DataFrame:
    """
    Simulates trading based on df['signal']: 
    - When signal=+1: go long one unit of the underlying
    - When signal=-1: go short one unit
    - Tracks cash, position, and portfolio_value over time
    - Applies transaction_cost as a fraction of trade value
    Returns DataFrame with columns ['cash', 'position', 'portfolio_value'].
    Raises ValueError if 'signal' or 'Close' columns are missing.
    """
    if 'signal' not in df.columns or 'Close' not in df.columns:
        raise ValueError("DataFrame must contain 'signal' and 'Close' columns.")

    df['position'] = df['signal'].shift(1).fillna(0)
    df['trade'] = df['position'].diff().fillna(0)
    df['cost'] = abs(df['trade']) * df['Close'] * transaction_cost
    df['cash'] = initial_cash - (df['trade'] * df['Close']).cumsum() - df['cost'].cumsum()
    df['portfolio_value'] = df['cash'] + df['position'] * df['Close']

    return df[['cash', 'position', 'portfolio_value']] 