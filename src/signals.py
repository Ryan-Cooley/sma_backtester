import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'signal' column: +1 when SMA_fast crosses above SMA_slow,
    -1 when SMA_fast crosses below SMA_slow, and 0 otherwise.
    Forward-fill the signal and set initial NaNs to 0.
    """
    if 'SMA_fast' not in df.columns or 'SMA_slow' not in df.columns:
        raise ValueError("DataFrame must contain 'SMA_fast' and 'SMA_slow' columns.")
    
    df['signal'] = 0
    df.loc[df['SMA_fast'] > df['SMA_slow'], 'signal'] = 1
    df.loc[df['SMA_fast'] < df['SMA_slow'], 'signal'] = -1
    df['signal'] = df['signal'].diff().fillna(0)
    df['signal'] = np.sign(df['signal'])
    
    return df 