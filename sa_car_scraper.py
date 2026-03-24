import pandas as pd
import time
from playwright.sync_api import sync_playwright

data = []

BASE_URL = "https://www.autotrader.co.za/cars-for-sale?pagenumber={}"

MAX_PAGES = 50   # start small for testing


def scrape_page(page):

    cars = page.query_selector_all("article")

    for car in cars:

        try:

            title_el = car.query_selector("h2")
            price_el = car.query_selector("[data-testid='vehicle-price']")

            if not title_el or not price_el:
                continue

            title = title_el.inner_text()
            price = price_el.inner_text()

            data.append({
                "title": title,
                "price": price
            })

        except:
            continue


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    for i in range(1, MAX_PAGES + 1):

        url = BASE_URL.format(i)

        print("Scraping page:", i)

        page.goto(url)

        page.wait_for_timeout(5000)

        scrape_page(page)

        time.sleep(2)

    browser.close()


df = pd.DataFrame(data)

df.to_csv("sa_car_listings.csv", index=False)

print("Total cars scraped:", len(df))