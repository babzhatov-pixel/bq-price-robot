from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import urllib.request
from io import StringIO

app = Flask(__name__)
CORS(app)

SHEET_ID = "1IVvCwJdkxtTNpWh8NKWloczlwuuqbyDcufe7uP9QAVM"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@app.route("/")
def home():
    return "BQ PRICE ROBOT SERVER IS WORKING"

@app.route("/price")
def price():
    query = request.args.get("product", "").lower()

    response = urllib.request.urlopen(SHEET_URL)
    data = response.read().decode("utf-8")
    reader = csv.DictReader(StringIO(data))

    for row in reader:
        product_name = row.get("Товар", "").lower()

        if query in product_name:
            return jsonify({
                "product": row.get("Товар", ""),
                "cash_price": row.get("Цена нал", ""),
                "kaspi_price": row.get("Наша цена Kaspi", ""),
                "stock": row.get("КОЛВО", ""),
                "pspdf_link": row.get("Ссылка pspdf", ""),
                "kaspi_link": row.get("Ссылка Kaspi", "")
            })

    return jsonify({
        "product": query,
        "cash_price": "Не найдено",
        "kaspi_price": "Не найдено",
        "stock": "0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)