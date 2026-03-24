import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

cars = []

headers = {
    "User-Agent": "Mozilla/5.0"
}

for page in range(1,50):

    url = f"https://www.gumtree.co.za/s-cars-vans-bakkies/page-{page}/v1c9078p{page}"

    print("Scraping page:", page)

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print("Failed page:", page)
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    listings = soup.find_all("div", {"class":"listing-item"})

    print("Listings found:", len(listings))

    for car in listings:
        try:
            title = car.find("a", {"class":"listing-title"}).text.strip()

            price = car.find("span", {"class":"price"}).text.strip()

            location = car.find("span", {"class":"location"}).text.strip()

            cars.append({
                "title": title,
                "price": price,
                "location": location
            })

        except:
            pass

    time.sleep(2)

df = pd.DataFrame(cars)

df.to_csv("gumtree_sa_cars.csv", index=False)

print("Total cars scraped:", len(df))