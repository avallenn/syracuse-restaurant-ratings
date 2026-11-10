# Discover Syracuse Restaurants

A small data pipeline and Streamlit app built for IST 356 at Syracuse University. It scrapes TripAdvisor's list of popular restaurants in Syracuse, NY, cleans the data with Pandas, and lets you choose a food category to see matching restaurants and their average star rating by price category. The question it explores is whether price goes with better-rated food.

## What it does

1. **Scrape** (`src/scraper.py`): Playwright opens the archived TripAdvisor page and saves each restaurant's ranked name and the raw text listed under it (rating, review count, category, price) to `data/restaurants_raw.csv`.
2. **Clean** (`src/functions.py`): Pandas functions split out the ranking, numeric star rating, cuisine categories and price category, then write `data/restaurants_cleaned.csv`. Each step returns a new DataFrame; `clean_restaurants()` runs them in order.
3. **Explore** (`app.py`): a Streamlit app where you pick a category (Italian, Diner, Seafood, ...). It shows the matching restaurants, a bar chart of average stars per price category, and how many restaurants each average is based on.

Price categories map TripAdvisor's labels: `$` = Inexpensive, `$$ - $$$` = Moderate, `$$$$` = Expensive. Any other label is treated as missing and left out of averages.

## Data source

TripAdvisor blocks automated browsers, so the scraper reads a [Web Archive snapshot of the TripAdvisor Syracuse restaurants page from 7 May 2024](https://web.archive.org/web/20240507043028/www.tripadvisor.com/Restaurants-g48713-Syracuse_Finger_Lakes_New_York.html).

The snapshot lists 30 restaurants, so the averages are rough. Most restaurants are Moderate (24 of 30), with 4 Expensive and 2 Inexpensive. After filtering by category, some averages come from only one or two restaurants. Ratings are TripAdvisor's half-star scores, so the averages fall in a narrow range (4.0 to 5.0).

## How to run

Python 3.12 was used.

```bash
pip install -r requirements.txt
playwright install chromium
python -m src.scraper        # optional: re-scrapes and overwrites data/restaurants_raw.csv
python -m src.functions      # cleans data/restaurants_raw.csv -> data/restaurants_cleaned.csv
pytest
streamlit run app.py
```

Both CSVs are included, so you can skip the scraper. It opens a visible Chromium window. Its CSS selector is TripAdvisor's auto-generated class name from this one snapshot, so it will likely break on any other page.

## Project layout

```
app.py                  Streamlit app
src/scraper.py          Playwright scraper (Web Archive snapshot)
src/functions.py        Pandas cleaning functions + clean_restaurants()
tests/test_functions.py pytest tests for the cleaning functions
data/                   restaurants_raw.csv, restaurants_cleaned.csv
```
