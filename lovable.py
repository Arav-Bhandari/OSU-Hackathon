from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


BadNutrientKey = str  # "sodium" | "saturated_fat" | "trans_fat" | "cholesterol" | "sugars"
GoodNutrientKey = str  # "fiber" | "protein" | "vitamin_a" | "vitamin_c" | "calcium"
NutrientKey = str      # union of both


@dataclass
class FoodRecord:
    restaurant: str
    item: str
    calories: float
    sodium: float
    saturated_fat: float
    trans_fat: float
    cholesterol: float
    sugars: float
    fiber: float
    protein: float
    vitamin_a: float
    vitamin_c: float
    calcium: float


QuarticCoefficients = Tuple[float, float, float, float, float]  # a0..a4


@dataclass
class ItemScore:
    item: FoodRecord
    rawScore: float
    penalizedScore: float


@dataclass
class RestaurantScoreResult:
    restaurant: str
    itemCount: int
    score: float
    finalCoeffs: QuarticCoefficients
    items: List[ItemScore]


@dataclass
class AnalysisResult:
    restaurants: List[RestaurantScoreResult]
    minCalories: float
    maxCalories: float


def evaluate_quartic(coeffs: QuarticCoefficients, x: float) -> float:
    a0, a1, a2, a3, a4 = coeffs
    return a0 + a1 * x + a2 * x * x + a3 * x * x * x + a4 * x * x * x * x


def solve_normal_equations_5(A: List[List[float]], b: List[float]) -> QuarticCoefficients:
    n = 5
    # Gaussian elimination with partial pivoting (in-place, like TS version)
    for i in range(n):
        # Pivot
        max_row = i
        for r in range(i + 1, n):
            if abs(A[r][i]) > abs(A[max_row][i]):
                max_row = r

        if abs(A[max_row][i]) < 1e-12:
            # Singular or near-singular; fall back to zeros
            return (0.0, 0.0, 0.0, 0.0, 0.0)

        if max_row != i:
            A[i], A[max_row] = A[max_row], A[i]
            b[i], b[max_row] = b[max_row], b[i]

        pivot = A[i][i]
        for j in range(i, n):
            A[i][j] /= pivot
        b[i] /= pivot

        for r in range(n):
            if r == i:
                continue
            factor = A[r][i]
            if abs(factor) < 1e-12:
                continue
            for c in range(i, n):
                A[r][c] -= factor * A[i][c]
            b[r] -= factor * b[i]

    return (b[0], b[1], b[2], b[3], b[4])


def fit_quartic(xs: List[float], ys: List[float]) -> QuarticCoefficients:
    n = len(xs)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0, 0.0)

    # Precompute sums of powers of x up to 8, and x^k * y up to 4
    s_x_pow = [0.0] * 9   # k=0..8
    s_xy_pow = [0.0] * 5  # k=0..4

    for x, y in zip(xs, ys):
        x_pow = 1.0
        for k in range(9):
            s_x_pow[k] += x_pow
            if k <= 4:
                s_xy_pow[k] += x_pow * y
            x_pow *= x

    A: List[List[float]] = [[0.0] * 5 for _ in range(5)]
    b: List[float] = [0.0] * 5

    for row in range(5):
        for col in range(5):
            A[row][col] = s_x_pow[row + col]
        b[row] = s_xy_pow[row]

    return solve_normal_equations_5(A, b)


def shift_quartic_to_min(coeffs: QuarticCoefficients, xs: List[float], target_min: float) -> QuarticCoefficients:
    if not xs:
        return coeffs

    min_y = float("inf")
    for x in xs:
        y = evaluate_quartic(coeffs, x)
        if y < min_y:
            min_y = y

    if not math.isfinite(min_y):
        return coeffs

    delta = target_min - min_y
    a0, a1, a2, a3, a4 = coeffs
    return (a0 + delta, a1, a2, a3, a4)


def shift_quartic_to_max(coeffs: QuarticCoefficients, xs: List[float], target_max: float) -> QuarticCoefficients:
    if not xs:
        return coeffs

    max_y = -float("inf")
    for x in xs:
        y = evaluate_quartic(coeffs, x)
        if y > max_y:
            max_y = y

    if not math.isfinite(max_y):
        return coeffs

    delta = target_max - max_y
    a0, a1, a2, a3, a4 = coeffs
    return (a0 + delta, a1, a2, a3, a4)


def add_quartic(a: QuarticCoefficients, b: QuarticCoefficients) -> QuarticCoefficients:
    return (
        a[0] + b[0],
        a[1] + b[1],
        a[2] + b[2],
        a[3] + b[3],
        a[4] + b[4],
    )


def penalty_factor(calories: float, raw_score: float) -> float:
    """
    New behavior:
    - If calories <= 2000: factor = 1
    - If calories > 2000 and raw_score >= 0: divide by log_5(c-2000)
      => factor = 1 / log_5(diff)
    - If calories > 2000 and raw_score < 0: multiply by log_25(c-2000)
      => factor = log_25(diff)
    """
    if calories <= 2000:
        return 1.0

    diff = calories - 2000.0

    log5 = math.log(diff, 5) if diff > 0 else float("nan")
    if not math.isfinite(log5) or log5 <= 0:
        return 1.0

    if raw_score >= 0:
        return 1.0 / log5

    log25 = math.log(diff, 25) if diff > 0 else float("nan")
    if not math.isfinite(log25) or log25 <= 0:
        return 1.0

    return log25


def safe_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator) or denominator == 0:
        return 0.0
    return numerator / denominator


def analyze_fast_food_data(records: List[FoodRecord]) -> Optional[AnalysisResult]:
    if not records:
        return None

    by_restaurant: Dict[str, List[FoodRecord]] = {}
    min_calories = float("inf")
    max_calories = -float("inf")

    for rec in records:
        by_restaurant.setdefault(rec.restaurant, []).append(rec)
        if rec.calories > 0:
            min_calories = min(min_calories, rec.calories)
            max_calories = max(max_calories, rec.calories)

    if not math.isfinite(min_calories) or not math.isfinite(max_calories):
        return None

    restaurants: List[RestaurantScoreResult] = []

    bad_keys: List[BadNutrientKey] = [
        "sodium",
        "saturated_fat",
        "trans_fat",
        "cholesterol",
        "sugars",
    ]
    good_keys: List[GoodNutrientKey] = [
        "fiber",
        "protein",
        "vitamin_a",
        "vitamin_c",
        "calcium",
    ]

    for restaurant, items in by_restaurant.items():
        xs_all = [i.calories for i in items if i.calories > 0]

        # Combined bad quartic
        combined_bad: QuarticCoefficients = (0.0, 0.0, 0.0, 0.0, 0.0)
        for key in bad_keys:
            xs: List[float] = []
            ys: List[float] = []
            for item in items:
                if item.calories <= 0:
                    continue
                x = item.calories
                y = safe_ratio(getattr(item, key), item.calories)
                xs.append(x)
                ys.append(y)
            if not xs:
                continue
            coeffs = fit_quartic(xs, ys)
            shifted = shift_quartic_to_min(coeffs, xs_all, -100.0)
            combined_bad = add_quartic(combined_bad, shifted)

        # Combined good quartic
        combined_good: QuarticCoefficients = (0.0, 0.0, 0.0, 0.0, 0.0)
        for key in good_keys:
            xs = []
            ys = []
            for item in items:
                if item.calories <= 0:
                    continue
                x = item.calories
                y = safe_ratio(getattr(item, key), item.calories)
                xs.append(x)
                ys.append(y)
            if not xs:
                continue
            coeffs = fit_quartic(xs, ys)
            shifted = shift_quartic_to_max(coeffs, xs_all, 100.0)
            combined_good = add_quartic(combined_good, shifted)

        final_coeffs = add_quartic(combined_bad, combined_good)

        item_scores: List[ItemScore] = []
        total_score = 0.0

        for item in items:
            raw = evaluate_quartic(final_coeffs, item.calories)
            pf = penalty_factor(item.calories, raw)
            penalized = raw * pf
            item_scores.append(ItemScore(item=item, rawScore=raw, penalizedScore=penalized))
            total_score += penalized

        restaurants.append(
            RestaurantScoreResult(
                restaurant=restaurant,
                itemCount=len(items),
                score=total_score,
                finalCoeffs=final_coeffs,
                items=item_scores,
            )
        )

    restaurants.sort(key=lambda r: r.score, reverse=True)

    return AnalysisResult(
        restaurants=restaurants,
        minCalories=min_calories,
        maxCalories=max_calories,
    )


def parse_fast_food_csv(csv_text: str) -> List[FoodRecord]:
    """
    Mirrors parseFastFoodCsv in TS:
    - Accepts headers:
      restaurant,
      item or item_name,
      calories,
      sodium,
      sat_fat or saturated_fat,
      trans_fat,
      cholesterol,
      sugar or sugars,
      fiber,
      protein,
      vit_a or vitamin_a,
      vit_c or vitamin_c,
      calcium
    """
    # Normalize lines: strip whitespace and skip empty
    lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
    if len(lines) < 2:
        return []

    # Use csv module to handle commas properly
    reader = csv.reader(lines)
    header_row = next(reader)
    header = [h.strip().lower() for h in header_row]

    def idx(name: str) -> int:
        try:
            return header.index(name)
        except ValueError:
            return -1

    col_restaurant = idx("restaurant")
    col_item = idx("item") if idx("item") != -1 else idx("item_name")
    col_calories = idx("calories")
    col_sodium = idx("sodium")
    col_sat_fat = idx("sat_fat") if idx("sat_fat") != -1 else idx("saturated_fat")
    col_trans_fat = idx("trans_fat")
    col_chol = idx("cholesterol")
    col_sugars = idx("sugar") if idx("sugar") != -1 else idx("sugars")
    col_fiber = idx("fiber")
    col_protein = idx("protein")
    col_vit_a = idx("vit_a") if idx("vit_a") != -1 else idx("vitamin_a")
    col_vit_c = idx("vit_c") if idx("vit_c") != -1 else idx("vitamin_c")
    col_calcium = idx("calcium")

    required = [
        col_restaurant,
        col_item,
        col_calories,
        col_sodium,
        col_sat_fat,
        col_trans_fat,
        col_chol,
        col_sugars,
        col_fiber,
        col_protein,
        col_vit_a,
        col_vit_c,
        col_calcium,
    ]

    if any(i == -1 for i in required):
        raise ValueError(
            "CSV must include headers at least: "
            "restaurant,item (or item_name),calories,sodium,"
            "sat_fat (or saturated_fat),trans_fat,cholesterol,"
            "sugar (or sugars),fiber,protein,vit_a (or vitamin_a),"
            "vit_c (or vitamin_c),calcium"
        )

    def to_num(v: str) -> float:
        v = v.strip()
        if not v:
            return 0.0
        try:
            n = float(v)
            return n if math.isfinite(n) else 0.0
        except ValueError:
            return 0.0

    records: List[FoodRecord] = []

    for parts in reader:
        # Ignore rows with mismatched column counts
        if len(parts) != len(header):
            continue

        restaurant = parts[col_restaurant].strip() if col_restaurant >= 0 else ""
        item = parts[col_item].strip() if col_item >= 0 else ""
        calories = to_num(parts[col_calories]) if col_calories >= 0 else 0.0

        if not restaurant or not item:
            continue

        records.append(
            FoodRecord(
                restaurant=restaurant,
                item=item,
                calories=calories,
                sodium=to_num(parts[col_sodium]),
                saturated_fat=to_num(parts[col_sat_fat]),
                trans_fat=to_num(parts[col_trans_fat]),
                cholesterol=to_num(parts[col_chol]),
                sugars=to_num(parts[col_sugars]),
                fiber=to_num(parts[col_fiber]),
                protein=to_num(parts[col_protein]),
                vitamin_a=to_num(parts[col_vit_a]),
                vitamin_c=to_num(parts[col_vit_c]),
                calcium=to_num(parts[col_calcium]),
            )
        )

    return records
