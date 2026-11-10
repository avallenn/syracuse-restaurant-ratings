"""Cleaning functions for the scraped TripAdvisor restaurant data.

Each step takes a DataFrame and returns a new one; the input is never modified.
`clean_restaurants()` runs every step in order.

Run `python -m src.functions` to read data/restaurants_raw.csv and write
data/restaurants_cleaned.csv.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_CSV = DATA_DIR / "restaurants_raw.csv"
CLEANED_CSV = DATA_DIR / "restaurants_cleaned.csv"

# TripAdvisor's price labels mapped to readable categories.
# Any other label becomes missing (NaN), so it is left out of averages.
PRICE_LABELS = {
    "$": "Inexpensive",
    "$$ - $$$": "Moderate",
    "$$$$": "Expensive",
}

# Open/closed status text that sits between the review count and the category.
STATUS_TEXT = ["Closed Now", "Closed Today", "Open Now"]

OUTPUT_COLUMNS = ["restaurant", "ranking", "stars", "category", "price"]


def extract_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Split '1. Apizza Regionale' into ranking=1 and restaurant='Apizza Regionale'.

    Only the first period (the one after the rank number) is used, so names
    that contain a period, like "St. Mary's", stay whole. A name without a
    leading rank number is kept as-is and gets a missing ranking.
    """
    df = df.copy()
    names = df["restaurant"].str.strip()
    parts = names.str.extract(r"^(\d+)\.\s*(.*)$")
    df["ranking"] = pd.to_numeric(parts[0], errors="coerce").astype("Int64")
    df["restaurant"] = parts[1].fillna(names)
    return df


def extract_stars(df: pd.DataFrame) -> pd.DataFrame:
    """Read the numeric rating from text like '4.5 of 5 bubbles...'."""
    df = df.copy()
    rating = df["information"].str.extract(r"^\s*(\d+(?:\.\d+)?) of 5", expand=False)
    df["stars"] = pd.to_numeric(rating, errors="coerce")
    return df


def extract_category(df: pd.DataFrame) -> pd.DataFrame:
    """Read the cuisine text between the review count and the price.

    '...268 reviewsClosed NowItalian, Pizza$$ - $$$Menu' -> 'Italian, Pizza'
    """
    df = df.copy()
    info = df["information"]
    for status in STATUS_TEXT:
        info = info.str.replace(status, " ", regex=False)
    category = info.str.split("reviews", n=1).str[1]
    category = category.str.split("$", n=1, regex=False).str[0]
    df["category"] = category.str.strip().str.replace(r"\s*,\s*", ", ", regex=True)
    return df


def extract_price(df: pd.DataFrame) -> pd.DataFrame:
    """Map TripAdvisor's price label ('$', '$$ - $$$', '$$$$') to a category."""
    df = df.copy()
    label = df["information"].str.extract(r"(\$+(?: - \$+)?)", expand=False)
    df["price"] = label.map(PRICE_LABELS)
    return df


def clean_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    """Run every cleaning step in order and drop the raw 'information' column."""
    cleaned = extract_ranking(df)
    cleaned = extract_stars(cleaned)
    cleaned = extract_category(cleaned)
    cleaned = extract_price(cleaned)
    return cleaned.drop(columns="information")[OUTPUT_COLUMNS]


if __name__ == "__main__":
    raw = pd.read_csv(RAW_CSV)
    cleaned = clean_restaurants(raw)
    cleaned.to_csv(CLEANED_CSV, index=False)

    print(f"Read {len(raw)} rows from {RAW_CSV}")
    print(f"Wrote {len(cleaned)} rows to {CLEANED_CSV}")
    missing = cleaned.isna().sum()
    if missing.any():
        print("Missing values per column:")
        print(missing[missing > 0].to_string())
