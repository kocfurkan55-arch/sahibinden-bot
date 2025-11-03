import requests
from bs4 import BeautifulSoup
import json
import time

search_urls = [
    "https://www.sahibinden.com/otomobil/citroen/c-elysee",
    "https://www.sahibinden.com/otomobil/peugeot/301"
]
pages_to_check = 50
telegram_token = "8385802559:AAHAaFagANyAz4ppbvwM3hae87CCcFInLE8"
chat_id = "5548796395"
price_file = "otomobil_fiyatlar.json"
wait_seconds = 60*60  # 1 hour

try:
    with open(price_file, "r") as f:
        previous_prices = json.load(f)
except:
    previous_prices = {}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

def get_listings(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = {}
    for listing in soup.find_all("tr", {"class": "searchResultsItem"}):
        try:
            listing_id = listing.get("data-id")
            price_tag = listing.find("td", {"class": "searchResultsPriceValue"})
            if listing_id and price_tag:
                price = price_tag.text.strip().replace(".", "").replace(" TL", "").replace(" ", "")
                listings[listing_id] = int(price)
        except:
            continue
    return listings

print("Bot started! Checking prices every hour...")

while True:
    for base_link in search_urls:
        for page in range(1, pages_to_check + 1):
            url = f"{base_link}?pagingOffset={(page-1)*50}"
            try:
                listings = get_listings(url)
            except:
                continue
            for listing_id, price in listings.items():
                previous_price = previous_prices.get(listing_id)
                listing_link = f"https://www.sahibinden.com/ilan/{listing_id}"
                if previous_price and price < previous_price:
                    message = f"Price dropped!\n{listing_link}\nOld: {previous_price} TL\nNew: {price} TL"
                    print(message)
                    send_telegram(message)
                previous_prices[listing_id] = price
            time.sleep(1)
    with open(price_file, "w") as f:
        json.dump(previous_prices, f)
    print("Waiting 1 hour...")
    time.sleep(wait_seconds)
