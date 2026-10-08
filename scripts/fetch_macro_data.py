import yfinance as yf
import pandas as pd
import os

def fetch_data():
    os.makedirs('data', exist_ok=True)
    
    tickers = {
        'BZ=F': 'data/brent_crude.csv',
        'DX-Y.NYB': 'data/dxy_index.csv'
    }
    
    for ticker, output_file in tickers.items():
        print(f"Fetching {ticker}...")
        data = yf.download(ticker, start="2017-09-01")
        if not data.empty:
            data.to_csv(output_file)
            print(f"Saved to {output_file}")
        else:
            print(f"Failed to fetch data for {ticker}")

if __name__ == "__main__":
    fetch_data()
