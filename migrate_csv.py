# migrate_csv.py
import pandas as pd
import os
import uuid
from config.config import Config

def migrate_csv():
    """Migrate existing CSV to new structure"""
    if not os.path.exists(Config.CSV_FILE):
        print("CSV file not found")
        return
    
    try:
        df = pd.read_csv(Config.CSV_FILE)
        if df.empty:
            print("CSV is empty")
            return
        
        print(f"Original columns: {list(df.columns)}")
        print(f"Total records: {len(df)}")
        
        # Ensure all required columns exist
        for col in Config.CSV_COLUMNS:
            if col not in df.columns:
                df[col] = ''
        
        # Ensure each document has an ID
        for idx, row in df.iterrows():
            if pd.isna(row.get('id')) or row.get('id') == '':
                df.at[idx, 'id'] = str(uuid.uuid4())
            
            # Ensure document_type exists
            if pd.isna(row.get('document_type')) or row.get('document_type') == '':
                df.at[idx, 'document_type'] = 'rc'
            
            # Ensure title exists
            if pd.isna(row.get('title')) or row.get('title') == '':
                df.at[idx, 'title'] = row.get('original_name', 'Untitled')
            
            # Ensure amount is float
            try:
                amount = float(row.get('amount', 0))
                df.at[idx, 'amount'] = amount
            except (ValueError, TypeError):
                df.at[idx, 'amount'] = 0.0
            
            # Ensure download_count exists
            if pd.isna(row.get('download_count')):
                df.at[idx, 'download_count'] = 0
        
        # Save migrated data
        df.to_csv(Config.CSV_FILE, index=False)
        print(f"Migration complete. New columns: {list(df.columns)}")
        print(f"Total records after migration: {len(df)}")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_csv()
