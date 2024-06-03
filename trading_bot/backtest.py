import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from COCOPILOT.trading_bot.data.fetch_new_data import fetch_historical_data
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerStrategy
import logging

logging.basicConfig(level=logging.INFO)

def calculate_performance(df, initial_capital):
    df['portfolio_value'] = initial_capital * (1 + df['return']).cumprod()

    # Calculate ROI
    final_portfolio_value = df['portfolio_value'].iloc[-1]
    roi = (final_portfolio_value - initial_capital) / initial_capital

    # Calculate maximum drawdown
    cum_max = df['portfolio_value'].cummax()
    drawdown = (df['portfolio_value'] - cum_max) / cum_max
    max_drawdown = drawdown.min()

    # Calculate Sharpe ratio
    daily_return = df['return'].mean()
    daily_volatility = df['return'].std()
    sharpe_ratio = daily_return / daily_volatility * np.sqrt(252)

    return roi, max_drawdown, sharpe_ratio

def backtest_strategy(strategy, symbol, timeframe, start_date, end_date, initial_capital):
    historical_data = fetch_historical_data(symbol, timeframe, start_date, end_date)
    strategy_instance = strategy()
    historical_data['return'] = 0
    portfolio_value = initial_capital

    for i in range(1, len(historical_data)):
        market_data = historical_data.iloc[:i+1]
        decision = strategy_instance.decide(market_data)
        
        if decision == "BUY":
            historical_data.at[i, 'return'] = historical_data['close'].iloc[i] / historical_data['close'].iloc[i-1] - 1
        elif decision == "SELL":
            historical_data.at[i, 'return'] = historical_data['close'].iloc[i-1] / historical_data['close'].iloc[i] - 1

    roi, max_drawdown, sharpe_ratio = calculate_performance(historical_data, initial_capital)
    return roi, max_drawdown, sharpe_ratio

if __name__ == "__main__":
    symbol = "BTC/USDT"
    timeframe = "1h"
    start_date = "2024-01-01"
    end_date = "2024-01-07"
    initial_capital = 10000

    macd_roi, macd_max_drawdown, macd_sharpe_ratio = backtest_strategy(MACDStrategy, symbol, timeframe, start_date, end_date, initial_capital)
    bollinger_roi, bollinger_max_drawdown, bollinger_sharpe_ratio = backtest_strategy(BollingerStrategy, symbol, timeframe, start_date, end_date, initial_capital)

    logging.info(f"MACD Strategy Results: ROI = {macd_roi:.2%}, Max Drawdown = {macd_max_drawdown:.2%}, Sharpe Ratio = {macd_sharpe_ratio:.2f}")
    logging.info(f"Bollinger Strategy Results: ROI = {bollinger_roi:.2%}, Max Drawdown = {bollinger_max_drawdown:.2%}, Sharpe Ratio = {bollinger_sharpe_ratio:.2f}")
