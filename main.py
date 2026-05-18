from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import urllib.request
from io import StringIO
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
CORS(app)

SHEET_ID = "1IVvCwJdkxtTNpWh8NKWloczlwuuqbyDcufe7uP9QAVM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

KASPI_TOKEN = os.getenv("KASPI_API_TOKEN")

@app.route("/")
def home():
    return "BQ PRICE ROBOT SERVER IS WORKING"

def format_price(value):
    return f"{value:,}".replace(",", " ") + " ₸"

def parse_number(value):
    number = re.sub(r"\D", "", str(value))
    return int(number) if number else 0

# ---------- PSPDF ----------
def get_pspdf_price(url, min_price):
    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        all_text = soup.get_text(" ")

        prices = re.findall(r"\d[\d\s]{2,15}\s?₸", all_text)

        valid_prices = []

        for p in prices:

            value = parse_number(p)

            if value >= min_price and value < 5000000:
                valid_prices.append(value)

        if valid_prices:
            return format_price(min(valid_prices))

        return "Не найдено"

    except Exception:
        return "Ошибка"

# ---------- KASPI API ----------
def get_kaspi_price(product_name):

    try:

        headers = {
            "X-Auth-Token": KASPI_TOKEN,
            "Content-Type": "application/vnd.api+json"
        }

        response = requests.get(
            "https://kaspi.kz/shop/api/v2/products",
            headers=headers,
            timeout=20
        )

        data = response.json()

        products = data.get("data", [])

        for product in products:

            attributes = product.get("attributes", {})

            title = attributes.get("name", "").lower()

            if product_name.lower() in title:

                price = attributes.get("price", 0)

                return format_price(price)

        return "Не найдено"

    except Exception as e:

        return "Ошибка API"

# ---------- API ----------
@app.route("/price")
def price():

    query = request.args.get("product", "").lower()

    response = urllib.request.urlopen(SHEET_URL)

    data = response.read().decode("utf-8")

    reader = csv.DictReader(StringIO(data))

    for row in reader:

        product_name = row.get("Товар", "").lower()

        if query in product_name:

            pspdf_link = row.get("Ссылка pspdf", "")

            min_cash_price = parse_number(
                row.get("Минимальная цена наличка", "0")
            )

            live_cash_price = get_pspdf_price(
                pspdf_link,
                min_cash_price
            )

            live_kaspi_price = get_kaspi_price(
                row.get("Товар", "")
            )

            return jsonify({
                "product": row.get("Товар", ""),
                "cash_price": live_cash_price,
                "kaspi_price": live_kaspi_price,
                "stock": row.get("КОЛВО", "")
            })

    return jsonify({
        "product": query,
        "cash_price": "Не найдено",
        "kaspi_price": "Не найдено",
        "stock": "0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)