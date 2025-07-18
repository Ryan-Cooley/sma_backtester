import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_cumulative_return(portfolio: pd.Series) -> float:
    """
    Computes the cumulative return of the portfolio.
    """
    return (portfolio.iloc[-1] / portfolio.iloc[0]) - 1

def compute_sharpe_ratio(portfolio: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Computes the annualized Sharpe ratio of the portfolio.
    """
    returns = portfolio.pct_change().dropna()
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else np.nan

def compute_max_drawdown(portfolio: pd.Series) -> float:
    """
    Computes the maximum drawdown of the portfolio.
    """
    cumulative_max = portfolio.cummax()
    drawdown = (portfolio - cumulative_max) / cumulative_max
    return drawdown.min()

def plot_equity_curve(portfolio: pd.Series):
    """
    Uses matplotlib to plot portfolio cumulative value over time with labels.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio.index, portfolio.values, label='Equity Curve')
    plt.title('Portfolio Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_price_signals(df: pd.DataFrame):
    """
    Plots the price, SMAs, and buy/sell signals on a single chart.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Close'], label='Close Price', color='black', alpha=0.7)
    if 'SMA_fast' in df.columns:
        plt.plot(df.index, df['SMA_fast'], label='SMA Fast', color='blue', alpha=0.7)
    if 'SMA_slow' in df.columns:
        plt.plot(df.index, df['SMA_slow'], label='SMA Slow', color='red', alpha=0.7)
    # Mark buy/sell signals
    buy_signals = (df['signal'].diff() > 0)
    sell_signals = (df['signal'].diff() < 0)
    plt.scatter(df.index[buy_signals], df['Close'][buy_signals], marker='^', color='green', label='Buy Signal', s=100, zorder=5)
    plt.scatter(df.index[sell_signals], df['Close'][sell_signals], marker='v', color='red', label='Sell Signal', s=100, zorder=5)
    plt.title('Price, SMAs, and Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def print_metrics_table(portfolio: pd.Series):
    """
    Prints a summary table of key metrics.
    """
    cumulative_return = compute_cumulative_return(portfolio)
    sharpe = compute_sharpe_ratio(portfolio)
    max_dd = compute_max_drawdown(portfolio)
    print("\nPerformance Summary:")
    print("-------------------")
    print(f"Cumulative Return: {cumulative_return:.2%}")
    print(f"Sharpe Ratio:      {sharpe:.2f}")
    print(f"Max Drawdown:      {max_dd:.2%}")

def plot_drawdown(portfolio: pd.Series):
    """
    Plots the drawdown over time to visualize periods of decline.
    """
    cumulative_max = portfolio.cummax()
    drawdown = (portfolio - cumulative_max) / cumulative_max
    
    plt.figure(figsize=(12, 6))
    plt.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    plt.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
    plt.title('Portfolio Drawdown Over Time')
    plt.xlabel('Date')
    plt.ylabel('Drawdown')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_rolling_metrics(portfolio: pd.Series, window: int = 252):
    """
    Plots rolling Sharpe ratio and rolling volatility over time.
    """
    returns = portfolio.pct_change().dropna()
    rolling_sharpe = returns.rolling(window=window).mean() / returns.rolling(window=window).std() * np.sqrt(252)
    rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Rolling Sharpe Ratio
    ax1.plot(rolling_sharpe.index, rolling_sharpe.values, color='blue')
    ax1.set_title(f'Rolling Sharpe Ratio ({window}-day window)')
    ax1.set_ylabel('Sharpe Ratio')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Rolling Volatility
    ax2.plot(rolling_vol.index, rolling_vol.values, color='red')
    ax2.set_title(f'Rolling Volatility ({window}-day window)')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volatility')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_equity_with_signals(portfolio: pd.Series, df: pd.DataFrame):
    """
    Plots equity curve with buy/sell signal markers overlaid.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(portfolio.index, portfolio.values, label='Equity Curve', color='blue', linewidth=2)
    
    # Mark buy/sell signals on equity curve
    buy_signals = (df['signal'].diff() > 0)
    sell_signals = (df['signal'].diff() < 0)
    
    # Get portfolio values at signal points
    buy_values = portfolio[buy_signals]
    sell_values = portfolio[sell_signals]
    
    plt.scatter(buy_values.index, buy_values.values, marker='^', color='green', 
                label='Buy Signal', s=100, zorder=5)
    plt.scatter(sell_values.index, sell_values.values, marker='v', color='red', 
                label='Sell Signal', s=100, zorder=5)
    
    plt.title('Equity Curve with Trading Signals')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_comprehensive_dashboard(df: pd.DataFrame, portfolio: pd.Series, fast_sma: int = 20, slow_sma: int = 50, save_path: str = None):
    """
    Creates a comprehensive 4-panel dashboard similar to the interactive notebook.
    
    Args:
        df: DataFrame with price data and signals
        portfolio: Portfolio value series
        fast_sma: Fast SMA window for labeling
        slow_sma: Slow SMA window for labeling
        save_path: Optional path to save the plot image
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Panel 1: Price and signals
    ax1.plot(df.index, df['Close'], label='Close Price', alpha=0.7)
    if 'SMA_fast' in df.columns:
        ax1.plot(df.index, df['SMA_fast'], label=f'SMA {fast_sma}', alpha=0.7)
    if 'SMA_slow' in df.columns:
        ax1.plot(df.index, df['SMA_slow'], label=f'SMA {slow_sma}', alpha=0.7)
    
    # Mark signals
    buy_signals = (df['signal'].diff() > 0)
    sell_signals = (df['signal'].diff() < 0)
    ax1.scatter(df.index[buy_signals], df['Close'][buy_signals], marker='^', s=50, color='green', zorder=5, label='Buy')
    ax1.scatter(df.index[sell_signals], df['Close'][sell_signals], marker='v', s=50, color='red', zorder=5, label='Sell')
    ax1.set_title('Price and Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Equity curve
    ax2.plot(portfolio, linewidth=2)
    ax2.set_title('Portfolio Equity Curve')
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Drawdown
    cumulative_max = portfolio.cummax()
    drawdown = (portfolio - cumulative_max) / cumulative_max
    ax3.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
    ax3.plot(drawdown.index, drawdown.values, linewidth=1, color='red')
    ax3.set_title('Drawdown')
    ax3.grid(True, alpha=0.3)
    
    # Panel 4: Rolling Sharpe (if enough data)
    if len(portfolio) > 252:
        returns = portfolio.pct_change().dropna()
        rolling_sharpe = returns.rolling(252).mean() / returns.rolling(252).std() * np.sqrt(252)
        ax4.plot(rolling_sharpe.index, rolling_sharpe.values)
        ax4.axhline(y=0, linestyle='--', alpha=0.5)
        ax4.set_title('Rolling Sharpe Ratio (252-day)')
    else:
        ax4.text(0.5, 0.5, 'Insufficient data for rolling metrics', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('Rolling Metrics')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot if path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Dashboard saved to: {save_path}")
    
    plt.show()
    plt.show()

def compute_rolling_metrics(portfolio: pd.Series, window: int = 252) -> pd.DataFrame:
    """
    Computes rolling Sharpe ratio, volatility, and drawdown for analysis.
    Returns a DataFrame with rolling metrics.
    """
    returns = portfolio.pct_change().dropna()
    
    rolling_sharpe = returns.rolling(window=window).mean() / returns.rolling(window=window).std() * np.sqrt(252)
    rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
    
    cumulative_max = portfolio.cummax()
    rolling_dd = (portfolio - cumulative_max) / cumulative_max
    
    return pd.DataFrame({
        'Rolling_Sharpe': rolling_sharpe,
        'Rolling_Volatility': rolling_vol,
        'Rolling_Drawdown': rolling_dd
    })