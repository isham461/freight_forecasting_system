import pandas as pd
import os
import glob

def clean_numeric_col(series):
    """Removes commas from string representations of numbers and converts to float."""
    if series.dtype == 'object':
        return series.str.replace(',', '', regex=False).astype(float, errors='ignore')
    return series

def load_and_clean(filepath, name_prefix=None, yfinance_multi=False):
    if not os.path.exists(filepath):
        print(f"Warning: File {filepath} not found.")
        return pd.DataFrame()
        
    if yfinance_multi:
        df = pd.read_csv(filepath, header=[0, 1], index_col=0)
        df = df.reset_index()
        # Flatten MultiIndex and rename first col to Date
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df = df.rename(columns={df.columns[0]: 'Date'})
    else:
        df = pd.read_csv(filepath)
    
    # Standardize Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
    
    # Clean numeric columns
    for col in df.columns:
        if col != 'Date':
            # It might have strings like "3,157.00"
            if df[col].dtype == 'object':
                df[col] = clean_numeric_col(df[col])
            # Optional: prefix column names to distinguish them after merge
            if name_prefix:
                df = df.rename(columns={col: f"{name_prefix}_{col}"})
                
    return df

def main():
    print("Starting data merge process...")
    
    # 1. Load Macro Data
    brent = load_and_clean('data/brent_crude.csv', name_prefix='Brent', yfinance_multi=True)
    dxy = load_and_clean('data/dxy_index.csv', name_prefix='DXY', yfinance_multi=True)
    
    # 2. Load and merge Baltic Capesize Data
    capesize_files = [
        'Baltic Capesize Historical Data-2.csv',
        'Baltic Capesize Historical Data.csv',
        'data/baltic_capesize_2026.csv'
    ]
    
    capesize_dfs = []
    for f in capesize_files:
        df = load_and_clean(f)
        if not df.empty:
            capesize_dfs.append(df)
            
    if capesize_dfs:
        capesize = pd.concat(capesize_dfs, ignore_index=True)
        # Drop duplicates on Date, keeping the last (most recent/updated)
        capesize = capesize.drop_duplicates(subset=['Date'], keep='last')
        # Prefix columns
        capesize = capesize.rename(columns={col: f"Capesize_{col}" for col in capesize.columns if col != 'Date'})
    else:
        capesize = pd.DataFrame(columns=['Date'])
        
    # 3. Load Baltic Dry Index Data
    bdi = load_and_clean('Baltic Dry Index Historical Data-2.csv', name_prefix='BDI')
    
    # 4. Merge all on Date using outer join
    # Start with a master timeline based on all unique dates
    dfs = [df for df in [bdi, capesize, brent, dxy] if not df.empty]
    
    if not dfs:
        print("No data available to merge.")
        return
        
    master = dfs[0]
    for df in dfs[1:]:
        master = pd.merge(master, df, on='Date', how='outer')
        
    # Sort by date
    master = master.sort_values('Date').reset_index(drop=True)
    
    # 5. Handle missing values for weekends and non-trading days
    # Forward fill first, then backward fill for any leading NaNs
    master = master.ffill().bfill()
    
    # 6. Save to CSV
    out_path = 'data/master_freight_timeseries.csv'
    master.to_csv(out_path, index=False)
    
    print("\n--- MASTER DATASET INFO ---")
    master.info()
    
    # Show that there are zero missing values
    missing = master.isna().sum().sum()
    print(f"\nTotal missing values after ffill/bfill: {missing}")
    print(f"Dataset successfully saved to {out_path}")

if __name__ == "__main__":
    main()
