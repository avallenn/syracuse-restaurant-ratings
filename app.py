"""Streamlit app: browse Syracuse restaurants by food category and compare
average ratings by price category.

Run with: streamlit run app.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

CLEANED_CSV = Path(__file__).resolve().parent / 'data' / 'restaurants_cleaned.csv'
PRICE_ORDER = ['Inexpensive', 'Moderate', 'Expensive']


def split_categories(value) -> list[str]:
    """'Italian, Pizza' -> ['Italian', 'Pizza']"""
    if pd.isna(value):
        return []
    return [part.strip() for part in value.split(',') if part.strip()]


df = pd.read_csv(CLEANED_CSV)
df['category_list'] = df['category'].apply(split_categories)

st.title('Discover Syracuse Restaurants')
st.caption(
    f"Data: TripAdvisor's Syracuse restaurant list from a Web Archive snapshot "
    f"(May 2024), {len(df)} restaurants."
)

category_options = sorted({cat for cats in df['category_list'] for cat in cats})
category = st.selectbox('What type of food sounds good?', category_options)

if category:
    # Exact match on each listed category (str.contains would also match substrings).
    filtered_df = df[df['category_list'].apply(lambda cats: category in cats)]

    st.write(f'Here are your options for {category}!')
    st.dataframe(
        filtered_df[['ranking', 'restaurant', 'stars', 'category', 'price']],
        hide_index=True,
    )

    st.header('Average Rating by Price Category')

    # Restaurants with a missing price are left out of the averages.
    summary = (
        filtered_df.dropna(subset=['price'])
        .groupby('price')['stars']
        .agg(average_stars='mean', restaurants='count')
        .reindex(PRICE_ORDER)
        .dropna(subset=['average_stars'])
    )
    summary['restaurants'] = summary['restaurants'].astype(int)
    missing_price = int(filtered_df['price'].isna().sum())

    if summary.empty:
        st.write(f'None of the {category} restaurants have a listed price.')
    else:
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            bars = ax.bar(summary.index, summary['average_stars'])
            ax.bar_label(
                bars,
                labels=[f'{avg:.2f}\n(n={n})' for avg, n in zip(summary['average_stars'], summary['restaurants'])],
                label_type='center',
                color='white',
            )
            ax.set_ylim(0, 5)
            ax.set_xlabel('Price category')
            ax.set_ylabel('Average stars (out of 5)')
            st.pyplot(fig)

        with col2:
            st.dataframe(
                summary.round(2).rename_axis('Price').rename(columns={
                    'average_stars': 'Average stars',
                    'restaurants': 'Restaurants',
                }),
            )

            best = summary['average_stars'].max()
            top_prices = summary.index[np.isclose(summary['average_stars'], best)].tolist()
            if len(summary) == 1:
                st.write(
                    f'Every {category} restaurant with a listed price is {top_prices[0]}, '
                    f'so there is no other price category to compare it with.'
                )
            elif len(top_prices) > 1:
                st.write(
                    f"{' and '.join(top_prices)} tie for the highest average rating "
                    f"({best:.2f}), so price doesn't separate them for {category} restaurants."
                )
            else:
                n = summary.loc[top_prices[0], 'restaurants']
                st.write(
                    f'The suggested price category for {category} is {top_prices[0]}, '
                    f"with an average rating of {best:.2f} across {n} "
                    f"restaurant{'s' if n != 1 else ''}."
                )

        st.caption(
            f'Note: these averages are based on few restaurants (n is shown for each '
            f'price category; the whole dataset has {len(df)}), so treat differences '
            f"as rough, not conclusive. Ratings are TripAdvisor's half-star scores."
        )
        if missing_price:
            st.caption(f'{missing_price} restaurant(s) with no listed price are not included in the averages.')
