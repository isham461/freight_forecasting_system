import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def feature_engineering():
    # 1. Load the data
    df = pd.read_csv('data/master_freight_timeseries.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sort chronologically just to be safe
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Target variables (shift backwards since we want to predict future values)
    print("Creating target variables...")
    df['target_7d'] = df['Capesize_Price'].shift(-7)
    df['target_14d'] = df['Capesize_Price'].shift(-14)
    df['target_30d'] = df['Capesize_Price'].shift(-30)
    
    # Lag features
    print("Creating lag features...")
    lags = [1, 3, 7, 14, 30]
    for lag in lags:
        df[f'Capesize_lag_{lag}d'] = df['Capesize_Price'].shift(lag)
        
    # Momentum / Rolling Stats for Capesize and BDI
    print("Creating rolling statistics...")
    windows = [7, 30]
    for w in windows:
        # Capesize
        df[f'Capesize_sma_{w}d'] = df['Capesize_Price'].rolling(window=w).mean()
        df[f'Capesize_std_{w}d'] = df['Capesize_Price'].rolling(window=w).std()
        
        # BDI
        df[f'BDI_sma_{w}d'] = df['BDI_Price'].rolling(window=w).mean()
        df[f'BDI_std_{w}d'] = df['BDI_Price'].rolling(window=w).std()

    # Macro ratios
    print("Calculating macro ratios...")
    # Ratio of Capesize Spot Price to Brent Crude Price (Vessel Earnings vs. Fuel Burn)
    # Using Brent_Close
    df['Capesize_to_Brent_ratio'] = df['Capesize_Price'] / df['Brent_Close']
    
    # Calendar features
    print("Extracting calendar features...")
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    
    # Correlation Heatmap
    print("Generating correlation heatmap...")
    # Select a subset of important numerical features for the heatmap to remain legible
    features_for_corr = [
        'Capesize_Price', 'BDI_Price', 'Brent_Close', 'DXY_Close',
        'Capesize_lag_7d', 'Capesize_sma_7d', 'Capesize_std_7d',
        'Capesize_to_Brent_ratio', 
        'target_7d', 'target_14d', 'target_30d'
    ]
    
    corr_matrix = df[features_for_corr].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
    plt.title('Freight Time-Series Feature Correlation')
    plt.tight_layout()
    plt.savefig('data/correlation_heatmap.png')
    plt.close()
    
    # Save Finalized Dataset
    out_path = 'data/featured_freight_data.csv'
    df.to_csv(out_path, index=False)
    print(f"\nFeature engineering complete! Saved final dataset to {out_path}")
    print(f"Generated heatmap at data/correlation_heatmap.png")
    
    print("\nSample of engineered dataset:")
    print(df[['Date', 'Capesize_Price', 'Capesize_to_Brent_ratio', 'Capesize_sma_7d', 'target_7d']].tail(10))

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    feature_engineering()
