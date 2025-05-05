import pandas as pd
import constant

def get_prompt(region, specialty):
    sheet_id = constant.SHEET_ID
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv')

    # Trim column names
    search_key = f'{region} + {specialty}'.strip()

    # Check if the column exists
    if search_key in df.columns:
        if len(df) >= 0:  # Ensure there is a second row
            return df[search_key].iloc[0]  # Get value from second row (index 1)
        else:
            print(f"Warning: Column '{search_key}' exists but has no second row.")
            return None  # Or return a default value

    print(f"Error: Column '{search_key}' not found in the sheet.")
    return None  # Column not found
