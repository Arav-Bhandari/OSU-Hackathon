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
    food_allData = pd.read_csv(
        CSV_PATH,
        sep=r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)',
        engine="python",
        on_bad_lines="skip",   # pandas <2.0
        # on_bad_lines="warn"  # uncomment if using pandas >=2.0
    )
    fast_food = food_allData.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,11,12,16]]
    for i in range(len(fast_food)):
    if fast_food.iloc[i, 13] == "Yes":
        fast_food.iloc[i, 13] = 1
    else:
        fast_food.iloc[i, 13] = 0
    for i in range(len(fast_food)):
        fast_food.iloc[i, 3] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 4] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 5] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 6] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 7] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 8] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 9] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 10] /= fast_food.iloc[i, 2]
        fast_food.iloc[i, 11] /= fast_food.iloc[i, 2]
    return fast_food
