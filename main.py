from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "BQ PRICE ROBOT SERVER IS WORKING"

@app.route("/price")
def price():
    product = request.args.get("product", "NO PRODUCT")

    return jsonify({
        "product": product,
        "cash_price": "900 000 ₸",
        "kaspi_price": "950 000 ₸"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)