import os
import csv
import asyncio
from pathlib import Path

PATH = "data/fastfood.csv"
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

with open(PATH, 'r') as file:
   reader = csv.reader(file)
   for row in reader:
       print(row)