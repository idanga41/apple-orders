from flask import Flask, jsonify,request

app = Flask(__name__)

products = [
    {
        "sku": "APL-IPH15-256-BLK",
        "name": "iPhone 15 Pro",
        "storage": "256GB",
        "connectivity": "5G",
        "colour": "Space Black",
        "stock": 5
    },
    {
        "sku": "APL-IPAD-AIR-128-BLU",
        "name": "iPad Air",
        "storage": "128GB",
        "connectivity": "WiFi + Cellular",
        "colour": "Blue",
        "stock": 3
    },
    {
        "sku": "APL-MBP-14-1TB-SLV",
        "name": "MacBook Pro",
        "storage": "1TB",
        "connectivity": "WiFi",
        "colour": "Silver",
        "stock": 0
    }
]

@app.route('/')
def home():
    return "Welcome to Apple Orders API"

@app.route('/products')
def get_products():
    return jsonify(products)

@app.route('/order', methods=['POST'])
def place_order():
    data = request.get_json()
    sku = data.get('sku')
    customer_name = data.get('customer_name')
    product = next((p for p in products if p["sku"] == sku), None)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404
    if product["stock"] <= 0:
        return jsonify({"status": "error", "message": f"{product['name']} is out of stock"}), 400
    product["stock"] -= 1
    return jsonify({
        "status": "success",
        "message": f"Order received for {product['name']} by {customer_name}"
    }), 200



if __name__ == '__main__':
    app.run(debug=True)
