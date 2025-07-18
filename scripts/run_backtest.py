#!/usr/bin/env python3
"""
SMA Crossover Backtester CLI

Usage:
    python run_backtest.py --ticker SPY \
        --start 2015-01-01 --end 2024-01-01 --fast 20 --slow 50
    python run_backtest.py --ticker QQQ \
        --fast 10 --slow 30 --cash 50000
"""

import argparse
import sys
import os
from datetime import datetime
import pandas as pd

from data_loader import fetch_data
from indicators import compute_sma
from signals import generate_signals
from backtester import backtest_signals
from metrics import (
    compute_cumulative_return,
    compute_sharpe_ratio,
    compute_max_drawdown,
    plot_comprehensive_dashboard,
)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_backtest(
    ticker,
    start_date,
    end_date,
    fast_sma,
    slow_sma,
    initial_cash,
    transaction_cost,
    verbose=True,
):
    """
    Run SMA crossover backtest with given parameters.

    Returns:
        dict: Dictionary containing backtest results and metrics
    """

    if fast_sma >= slow_sma:
        raise ValueError("Fast SMA must be less than Slow SMA")

    if verbose:
        print(f"Running backtest for {ticker}")
        print(f"Date range: {start_date} to {end_date}")
        print(f"SMA pair: {fast_sma}/{slow_sma}")
        print(f"Initial cash: ${initial_cash:,.0f}")
        print(f"Transaction cost: {transaction_cost:.4f}")
        print("-" * 50)

    # Fetch data
    df = fetch_data(ticker, start_date, end_date)

    # Compute SMAs and signals
    df['SMA_fast'] = compute_sma(df, fast_sma)
    df['SMA_slow'] = compute_sma(df, slow_sma)
    df = generate_signals(df)

    # Run backtest
    results = backtest_signals(
        df, initial_cash=initial_cash, transaction_cost=transaction_cost
    )

    # Calculate metrics
    portfolio = results['portfolio_value']
    cum_ret = compute_cumulative_return(portfolio)
    sharpe = compute_sharpe_ratio(portfolio)
    max_dd = compute_max_drawdown(portfolio)
    final_value = portfolio.iloc[-1]

    # Calculate additional metrics
    total_return = final_value - initial_cash
    num_trades = abs(df['signal'].diff()).sum()

    # Calculate Win Rate
    # Find trade entry/exit points
    trade_entries = df['signal'].diff() != 0
    trade_returns = []
    in_trade = False
    entry_price = 0
    for idx, row in df.iterrows():
        if row['signal'] != 0 and not in_trade:
            entry_price = row['Close']
            in_trade = True
        elif row['signal'] == 0 and in_trade:
            exit_price = row['Close']
            trade_returns.append(exit_price - entry_price if entry_price != 0 else 0)
            in_trade = False
    # If still in trade at end, close at last price
    if in_trade:
        exit_price = df['Close'].iloc[-1]
        trade_returns.append(exit_price - entry_price if entry_price != 0 else 0)
    if trade_returns:
        win_rate = sum([tr > 0 for tr in trade_returns]) / len(trade_returns)
    else:
        win_rate = float('nan')

    if verbose:
        print("Results:")
        print(f"  Cumulative Return: {cum_ret:.2%}")
        print(f"  Sharpe Ratio:      {sharpe:.2f}")
        print(f"  Max Drawdown:      {max_dd:.2%}")
        print(f"  Final Portfolio:   ${final_value:,.0f}")
        print(f"  Total Return:      ${total_return:,.0f}")
        print(f"  Number of Trades:  {num_trades}")
        print(f"  Win Rate:          {win_rate:.2%}")
        print(f"  Data Points:       {len(df)}")

    return {
        'ticker': ticker,
        'start_date': start_date,
        'end_date': end_date,
        'fast_sma': fast_sma,
        'slow_sma': slow_sma,
        'initial_cash': initial_cash,
        'transaction_cost': transaction_cost,
        'cumulative_return': cum_ret,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'final_value': final_value,
        'total_return': total_return,
        'num_trades': num_trades,
        'win_rate': win_rate,
        'data_points': len(df),
    }


def run_grid_search(
    ticker,
    start_date,
    end_date,
    fast_smas,
    slow_smas,
    initial_cash,
    transaction_cost,
):
    """
    Run grid search over multiple SMA pairs.
    """
    results = []

    print(f"Running grid search for {ticker}")
    print(f"Testing {len(fast_smas) * len(slow_smas)} SMA combinations")
    print("-" * 50)

    for fast in fast_smas:
        for slow in slow_smas:
            if fast >= slow:
                continue
            try:
                result = run_backtest(
                    ticker,
                    start_date,
                    end_date,
                    fast,
                    slow,
                    initial_cash,
                    transaction_cost,
                    verbose=False,
                )
                results.append(result)
                print(
                    f"SMA {fast}/{slow}: Return {result['cumulative_return']:.2%}, "
                    f"Sharpe {result['sharpe_ratio']:.2f}, "
                    f"DD {result['max_drawdown']:.2%}"
                )
            except Exception as e:
                print(f"Error with SMA {fast}/{slow}: {e}")

    # Sort by Sharpe ratio
    results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)

    print(
        "\n" + "=" * 50
    )
    print("TOP 5 PERFORMING STRATEGIES:")
    print("=" * 50)

    for i, result in enumerate(results[:5]):
        print(
            f"{i+1}. SMA {result['fast_sma']}/{result['slow_sma']}: "
            f"Return {result['cumulative_return']:.2%}, "
            f"Sharpe {result['sharpe_ratio']:.2f}, "
            f"DD {result['max_drawdown']:.2%}"
        )

    return results


def main():
    parser = argparse.ArgumentParser(description='SMA Crossover Backtester CLI')
    parser.add_argument('--ticker', default='SPY', help='Stock ticker symbol')
    parser.add_argument('--start', default='2015-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', default=datetime.today().strftime('%Y-%m-%d'), help='End date (YYYY-MM-DD)')
    parser.add_argument('--fast', type=int, default=20, help='Fast SMA window')
    parser.add_argument('--slow', type=int, default=50, help='Slow SMA window')
    parser.add_argument('--cash', type=int, default=100000, help='Initial cash')
    parser.add_argument('--cost', type=float, default=0.001, help='Transaction cost')
    parser.add_argument('--grid', action='store_true', help='Run grid search')
    parser.add_argument(
        '--fast-range', nargs=2, type=int, default=[10, 30],
        help='Fast SMA range for grid search (min max)'
    )
    parser.add_argument(
        '--slow-range', nargs=2, type=int, default=[50, 200],
        help='Slow SMA range for grid search (min max)'
    )
    parser.add_argument('--output', help='Output file for results (CSV)')
    parser.add_argument('--plot', action='store_true', help='Generate comprehensive dashboard plot')

    args = parser.parse_args()

    try:
        if args.grid:
            # Grid search
            fast_smas = range(args.fast_range[0], args.fast_range[1] + 1, 5)
            slow_smas = range(args.slow_range[0], args.slow_range[1] + 1, 10)
            results = run_grid_search(
                args.ticker,
                args.start,
                args.end,
                fast_smas,
                slow_smas,
                args.cash,
                args.cost,
            )

            if args.output:
                df_results = pd.DataFrame(results)
                df_results.to_csv(args.output, index=False)
                print(
                    f"\nResults saved to {args.output}"
                )
        else:
            # Single backtest
            result = run_backtest(
                args.ticker,
                args.start,
                args.end,
                args.fast,
                args.slow,
                args.cash,
                args.cost,
            )

            # Generate plot if requested
            if args.plot:
                print("\nGenerating comprehensive dashboard...")
                # Re-run backtest to get the full dataframe for plotting
                df = fetch_data(args.ticker, args.start, args.end)
                df['SMA_fast'] = compute_sma(df, args.fast)
                df['SMA_slow'] = compute_sma(df, args.slow)
                df = generate_signals(df)
                results = backtest_signals(
                    df, initial_cash=args.cash, transaction_cost=args.cost
                )

                # Create images directory if it doesn't exist
                os.makedirs('images', exist_ok=True)

                # Save the dashboard plot
                plot_filename = f"images/sma_dashboard_{args.ticker}_{args.fast}_{args.slow}.png"
                plot_comprehensive_dashboard(
                    df, results['portfolio_value'], args.fast, args.slow, save_path=plot_filename
                )

            if args.output:
                df_result = pd.DataFrame([result])
                df_result.to_csv(args.output, index=False)
                print(
                    f"\nResults saved to {args.output}"
                )

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
