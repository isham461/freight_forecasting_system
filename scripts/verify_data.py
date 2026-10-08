import pandas as pd
import os

def check_dates(df, name):
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    print(f"- {name}: {len(df)} records | {min_date.date()} to {max_date.date()}")
    return min_date, max_date

def main():
    print("=== DATA VERIFICATION SUMMARY ===")
    
    # 1. Check Macro Data
    print("\n--- MACRO DATA (2017-Present) ---")
    brent = pd.read_csv('data/brent_crude.csv', header=[0, 1], index_col=0)
    brent = brent.reset_index()
    brent = brent.rename(columns={'index': 'Date', 'Price': 'Date'})
    # Because of multi-index, the first column after reset_index might be a tuple ('Date', '')
    if isinstance(brent.columns[0], tuple):
        brent.columns = [col[0] if isinstance(col, tuple) else col for col in brent.columns]
    brent['Date'] = pd.to_datetime(brent['Date'])
    check_dates(brent, "Brent Crude Oil")
    
    dxy = pd.read_csv('data/dxy_index.csv', header=[0, 1], index_col=0)
    dxy = dxy.reset_index()
    if isinstance(dxy.columns[0], tuple):
        dxy.columns = [col[0] if isinstance(col, tuple) else col for col in dxy.columns]
    dxy['Date'] = pd.to_datetime(dxy['Date'])
    check_dates(dxy, "US Dollar Index")

    # 2. Check Baltic Capesize
    print("\n--- BALTIC CAPESIZE DATA ---")
    bci_parts = []
    
    file1 = 'Baltic Capesize Historical Data-2.csv'
    if os.path.exists(file1):
        df1 = pd.read_csv(file1)
        df1['Date'] = pd.to_datetime(df1['Date'])
        check_dates(df1, "Historical Data (2017-2022)")
        bci_parts.append(df1)
    
    file2 = 'Baltic Capesize Historical Data.csv'
    if os.path.exists(file2):
        df2 = pd.read_csv(file2)
        df2['Date'] = pd.to_datetime(df2['Date'])
        check_dates(df2, "Historical Data (2022-2025)")
        bci_parts.append(df2)
        
    file3 = 'data/baltic_capesize_2026.csv'
    if os.path.exists(file3):
        df3 = pd.read_csv(file3)
        df3['Date'] = pd.to_datetime(df3['Date'])
        check_dates(df3, "2026 Scraped/Synthetic Data")
        bci_parts.append(df3)
        
    if bci_parts:
        combined = pd.concat(bci_parts, ignore_index=True)
        # Drop duplicates based on Date
        combined = combined.drop_duplicates(subset=['Date']).sort_values('Date')
        print("\n--- OVERALL BALTIC CAPESIZE ---")
        check_dates(combined, "Combined Baltic Capesize Data")
        
        # Verify continuity
        start_year = combined['Date'].min().year
        end_year = combined['Date'].max().year
        print(f"\nVerification: Covers from {start_year} to late {end_year}")
        if start_year <= 2017 and end_year >= 2026:
            print("Status: SUCCESS! All requested dates from 2017 to late 2026 are covered.")
        else:
            print("Status: INCOMPLETE! Some date ranges are missing.")
    else:
        print("No Baltic Capesize data found.")

if __name__ == "__main__":
    main()
