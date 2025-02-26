import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys

def get_stock_data(symbol, timeframe='1d', period='1y'):
    """
    Fetch stock data for the given symbol with specified timeframe and period
    """
    stock = yf.Ticker(symbol)
    
    timeframe_mapping = {
        '1m': '7d',
        '5m': '60d',
        '15m': '60d',
        '30m': '60d',
        '1h': '730d',
        '4h': '730d',
        '1d': period,
        '1wk': period,
        '1mo': period
    }
    
    selected_period = timeframe_mapping.get(timeframe, '1y')
    data = stock.history(period=selected_period, interval=timeframe)
    return data['Close']

def calculate_correlation(symbol1, symbol2, timeframe='1d', period='1y'):
    """
    Calculate Pearson's correlation between two stock symbols with specified timeframe
    """
    try:
        stock1_data = get_stock_data(symbol1, timeframe, period)
        stock2_data = get_stock_data(symbol2, timeframe, period)
        
        combined_data = pd.concat([stock1_data, stock2_data], axis=1, join='inner')
        combined_data.columns = [symbol1, symbol2]
        
        correlation = combined_data[symbol1].corr(combined_data[symbol2], method='pearson')
        return correlation
    
    except Exception as e:
        return f"Error: {str(e)}"

def continuous_monitor(symbol1, symbol2, timeframe='1d', period='1y'):
    """
    Continuously monitor and update correlation every minute when new data is available
    """
    last_update = None
    last_data_count = None
    
    while True:
        try:
            # Get current data
            stock1_data = get_stock_data(symbol1, timeframe, period)
            current_count = len(stock1_data)
            
            # Get current time
            current_time = datetime.now()
            
            # Check if it's time for a minute update and if new data is available
            if (last_update is None or 
                (current_time - last_update).total_seconds() >= 60) and \
               (last_data_count is None or current_count > last_data_count):
                
                correlation = calculate_correlation(symbol1, symbol2, timeframe, period)
                
                if isinstance(correlation, float):
                    print(f"\n! New data update at {current_time.strftime('%H:%M:%S')}")
                    print(f"Pearson's correlation between {symbol1} and {symbol2}: {correlation:.4f}")
                    print(f"Timeframe: {timeframe}")
                    if timeframe in ['1d', '1wk', '1mo']:
                        print(f"Period: {period}")
                    else:
                        print(f"Period: Automatically set based on timeframe")
                    sys.stdout.flush()
                    
                    last_update = current_time
                    last_data_count = current_count
                else:
                    print(f"\nError at {current_time.strftime('%H:%M:%S')}: {correlation}")
                    sys.stdout.flush()
            
            # Wait 5 seconds before next check
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"\nUnexpected error at {datetime.now().strftime('%H:%M:%S')}: {str(e)}")
            time.sleep(5)  # Wait before retrying

def main():
    """
    Main function to handle user input and start continuous monitoring
    """
    print("Stock Correlation Calculator - Continuous Monitoring")
    print("Enter stock symbols in uppercase (e.g., AAPL for Apple)")
    
    # Get user input
    symbol1 = input("Enter first stock symbol: ").strip().upper()
    symbol2 = input("Enter second stock symbol: ").strip().upper()
    
    print("\nAvailable timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo")
    timeframe = input("Enter timeframe (default is 1d): ").strip().lower() or '1d'
    
    valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo']
    if timeframe not in valid_timeframes:
        print(f"Invalid timeframe. Using default '1d'")
        timeframe = '1d'
    
    if timeframe in ['1d', '1wk', '1mo']:
        print("\nAvailable periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
        period = input("Enter period (default is 1y): ").strip().lower() or '1y'
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if period not in valid_periods:
            print(f"Invalid period. Using default '1y'")
            period = '1y'
    else:
        period = '1y'
    
    print("\nStarting continuous monitoring... (Press Ctrl+C to stop)")
    print("Updates will occur every minute when new data is available")
    continuous_monitor(symbol1, symbol2, timeframe, period)

if __name__ == "__main__":
    try:
        import yfinance
        main()
    except ImportError:
        print("Error: Please install yfinance first")
        print("Run: pip install yfinance")