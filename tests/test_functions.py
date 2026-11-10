import pandas as pd
import pytest

from src.functions import (
    clean_restaurants,
    extract_category,
    extract_price,
    extract_ranking,
    extract_stars,
)


@pytest.fixture
def raw_df():
    """Three rows copied from data/restaurants_raw.csv. A new copy for every test."""
    return pd.DataFrame({
        "restaurant": [
            "1. Apizza Regionale",
            "8. Stella's Diner",
            "26. Arad Evans Inn",
        ],
        "information": [
            "5.0 of 5 bubbles268 reviewsClosed NowItalian, Pizza$$ - $$$Menu",
            "4.5 of 5 bubbles621 reviewsClosed NowAmerican, Diner$Menu",
            "4.5 of 5 bubbles188 reviewsClosed NowItalian, French$$$$6.4 miFayetteville",
        ],
    })


def test_extract_ranking(raw_df):
    result = extract_ranking(raw_df)
    assert result["ranking"].tolist() == [1, 8, 26]
    assert result["restaurant"].tolist() == [
        "Apizza Regionale", "Stella's Diner", "Arad Evans Inn",
    ]


def test_extract_ranking_keeps_periods_in_name():
    # Made-up name (not in the dataset) to check that only the first period is split.
    df = pd.DataFrame({"restaurant": ["12. St. Mary's Cafe"]})
    result = extract_ranking(df)
    assert result.loc[0, "ranking"] == 12
    assert result.loc[0, "restaurant"] == "St. Mary's Cafe"


def test_extract_stars_is_numeric(raw_df):
    result = extract_stars(raw_df)
    assert pd.api.types.is_numeric_dtype(result["stars"])
    assert result["stars"].tolist() == [5.0, 4.5, 4.5]


def test_extract_category_strips_whitespace(raw_df):
    result = extract_category(raw_df)
    assert result["category"].tolist() == [
        "Italian, Pizza", "American, Diner", "Italian, French",
    ]


def test_extract_category_handles_other_status_text():
    # Row 6 of the real data says "Closed Today" instead of "Closed Now".
    df = pd.DataFrame({
        "information": ["4.5 of 5 bubbles449 reviewsClosed TodayItalian$$ - $$$3.9 miLiverpool"],
    })
    assert extract_category(df).loc[0, "category"] == "Italian"


def test_extract_price(raw_df):
    result = extract_price(raw_df)
    assert result["price"].tolist() == ["Moderate", "Inexpensive", "Expensive"]


def test_extract_price_unknown_label_is_missing():
    # "$$" alone is not one of the three labels in the data, so it should be missing.
    df = pd.DataFrame({"information": ["4.0 of 5 bubbles10 reviewsAmerican$$Menu"]})
    assert pd.isna(extract_price(df).loc[0, "price"])


@pytest.mark.parametrize(
    "step", [extract_ranking, extract_stars, extract_category, extract_price, clean_restaurants]
)
def test_steps_do_not_modify_input(raw_df, step):
    before = raw_df.copy()
    step(raw_df)
    pd.testing.assert_frame_equal(raw_df, before)


def test_clean_restaurants(raw_df):
    result = clean_restaurants(raw_df)
    assert list(result.columns) == ["restaurant", "ranking", "stars", "category", "price"]
    assert "information" not in result.columns
    first = result.iloc[0]
    assert first["restaurant"] == "Apizza Regionale"
    assert first["ranking"] == 1
    assert first["stars"] == 5.0
    assert first["category"] == "Italian, Pizza"
    assert first["price"] == "Moderate"
