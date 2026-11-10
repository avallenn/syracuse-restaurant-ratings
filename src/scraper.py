"""Scrape Syracuse restaurants from a Web Archive snapshot of TripAdvisor.

TripAdvisor blocks automated browsers, so this reads the 7 May 2024 Web Archive
snapshot instead. Writes data/restaurants_raw.csv with two columns: the ranked
name ("1. Apizza Regionale") and the raw text that follows it (rating, review
count, category, price).

Run with: python -m src.scraper  (overwrites data/restaurants_raw.csv)
"""

import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import Playwright, sync_playwright

URL = 'https://web.archive.org/web/20240507043028/www.tripadvisor.com/Restaurants-g48713-Syracuse_Finger_Lakes_New_York.html'

# Brittle: these are TripAdvisor's auto-generated class names as they appear in
# this one snapshot. They carry no meaning and will likely break on any other
# snapshot or on the live site.
RESTAURANT_SELECTOR = 'div.VDEXx.u.Ff.K'

OUTPUT_CSV = Path(__file__).resolve().parent.parent / 'data' / 'restaurants_raw.csv'


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    page.wait_for_selector(RESTAURANT_SELECTOR)
    time.sleep(5)  # give the archived page time to finish rendering the list

    rows = []
    for restaurant in page.query_selector_all(RESTAURANT_SELECTOR):
        name = restaurant.inner_text()
        # The rating, category and price are in the element right after the name.
        # ElementHandle has no next_sibling, so read it with JavaScript
        # (written with help from GitHub Copilot).
        information = restaurant.evaluate('(element) => element.nextElementSibling.textContent')
        rows.append((name, information))

    context.close()
    browser.close()

    df = pd.DataFrame(rows, columns=['restaurant', 'information'])
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f'Wrote {len(df)} rows to {OUTPUT_CSV}')


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)
