from functools import lru_cache
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from src.analyzer import (
    FoodRecord, AnalysisResult, parse_fast_food_csv,
    analyze_fast_food_data, QuarticCoefficients, evaluate_quartic
)

DATA_DIR = Path(__file__).parent.parent / "data"
CSV_PATH = DATA_DIR / "fastfood.csv"


class DataService:
    _instance = None
    _df: Optional[pd.DataFrame] = None
    _records: Optional[List[FoodRecord]] = None
    _analysis: Optional[AnalysisResult] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    @lru_cache(maxsize=1)
    def df(self) -> pd.DataFrame:
        if self._df is None:
            self._load_data()
        return self._df
    
    @property
    def records(self) -> List[FoodRecord]:
        if self._records is None:
            self._load_data()
        return self._records
    
    @property
    def analysis(self) -> AnalysisResult:
        if self._analysis is None:
            self._load_data()
        return self._analysis
    
    def _load_data(self):
        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV not found at {CSV_PATH}")
        
        with open(CSV_PATH, 'r') as f:
            csv_text = f.read()
        
        self._records = parse_fast_food_csv(csv_text)
        self._analysis = analyze_fast_food_data(self._records)
        
        items_data = []
        for rec in self._records:
            items_data.append({
                'restaurant': rec.restaurant,
                'item': rec.item,
                'calories': rec.calories,
                'sodium': rec.sodium,
                'saturated_fat': rec.saturated_fat,
                'trans_fat': rec.trans_fat,
                'cholesterol': rec.cholesterol,
                'sugars': rec.sugars,
                'fiber': rec.fiber,
                'protein': rec.protein,
                'vitamin_a': rec.vitamin_a,
                'vitamin_c': rec.vitamin_c,
                'calcium': rec.calcium
            })
        self._df = pd.DataFrame(items_data)
    
    def get_restaurants(self) -> List[str]:
        return sorted(self.df['restaurant'].unique().tolist())
    
    def get_items_by_restaurant(self, restaurant: str) -> pd.DataFrame:
        return self.df[self.df['restaurant'] == restaurant]
    
    def filter_by_calories(self, min_cal: float, max_cal: float) -> pd.DataFrame:
        return self.df[(self.df['calories'] >= min_cal) & (self.df['calories'] <= max_cal)]
    
    def get_stats(self) -> Dict:
        return {
            'total_items': len(self.df),
            'total_restaurants': self.df['restaurant'].nunique(),
            'avg_calories': self.df['calories'].mean(),
            'avg_sodium': self.df['sodium'].mean(),
            'avg_protein': self.df['protein'].mean(),
            'min_calories': self.df['calories'].min(),
            'max_calories': self.df['calories'].max()
        }
    
    def get_restaurant_scores(self) -> List[Dict]:
        if not self.analysis:
            return []
        
        return [{
            'restaurant': r.restaurant,
            'score': r.score,
            'item_count': r.itemCount,
            'coefficients': r.finalCoeffs
        } for r in self.analysis.restaurants]


data_service = DataService()
