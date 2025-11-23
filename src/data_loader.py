# src/data_loader.py
import csv
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
CSV_PATH = DATA_DIR / "fastfood.csv"

def load_data() -> pd.DataFrame:
    """
    Loads the fastfood.csv file correctly even with quoted commas in item names.
    Returns a clean DataFrame with proper numeric types.
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")

    # This regex handles commas inside quotes perfectly
    df = pd.read_csv(
        CSV_PATH,
        sep=r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)',
        engine="python",
        on_bad_lines="skip",   # pandas <2.0
        # on_bad_lines="warn"  # uncomment if using pandas >=2.0
    )

    # Fix column names (strip whitespace)
    df.columns = [col.strip() for col in df.columns]

    # Convert numeric columns safely
    numeric_cols = [
        'calories', 'cal_fat', 'total_fat', 'sat_fat', 'trans_fat',
        'cholesterol', 'sodium', 'total_carb', 'fiber', 'sugar', 'protein',
        'vit_a', 'vit_c', 'calcium'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean item names (remove extra quotes)
    if 'item' in df.columns:
        df['item'] = df['item'].str.replace('"', '').str.strip()

    print(f"Loaded {len(df):,} menu items from {len(df['restaurant'].unique())} restaurants")
    return df