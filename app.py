from flask import Flask, request, jsonify
import random

app = Flask(__name__)

products = [
    {"sku": "APL-IPH15-256-BLK", "name": "iPhone 15 Pro", "storage": "256GB", "connectivity": "5G", "colour": "Space Black", "stock": 5},
    {"sku": "APL-IPAD-AIR-128-BLU", "name": "iPad Air", "storage": "128GB", "connectivity": "WiFi + Cellular", "colour": "Blue", "stock": 3},
    {"sku": "APL-MBP-14-1TB-SLV", "name": "MacBook Pro", "storage": "1TB", "connectivity": "WiFi", "colour": "Silver", "stock": 0}
]

orders = []
_next_id = 1

reviews = {}  # key = sku, value = list of {"rating": int, "comment": str}

@app.route("/")
def home():
    return "Welcome to Idan's Apple Orders API"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/products")
def get_products():
    return jsonify(products)

@app.route("/order", methods=["POST"])
def place_order_legacy():
    return _create_order()

@app.route("/orders", methods=["POST"])
def create_order():
    return _create_order()

@app.route("/orders", methods=["GET"])
def list_orders():
    return jsonify(orders)

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    o = next((o for o in orders if o["id"] == order_id), None)
    if not o:
        return jsonify({"status": "error", "message": "Order not found"}), 404
    return jsonify(o)

@app.route("/products/<sku>/reviews", methods=["GET"])
def get_reviews(sku):
    lst = reviews.get(sku, [])
    if not any(p for p in products if p["sku"] == sku):
        return jsonify({"status": "error", "message": "Product not found"}), 404
    if lst:
        avg = sum(r["rating"] for r in lst) / len(lst)
    else:
        avg = None
    return jsonify({"sku": sku, "avg_rating": avg, "count": len(lst), "reviews": lst})

@app.route("/products/<sku>/reviews", methods=["POST"])
def add_review(sku):
    if not any(p for p in products if p["sku"] == sku):
        return jsonify({"status": "error", "message": "Product not found"}), 404
    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    comment = (data.get("comment") or "").strip()
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"status": "error", "message": "rating must be integer 1..5"}), 400
    entry = {"rating": rating, "comment": comment}
    reviews.setdefault(sku, []).append(entry)
    lst = reviews[sku]
    avg = sum(r["rating"] for r in lst) / len(lst)
    return jsonify({"status": "success", "sku": sku, "avg_rating": avg, "count": len(lst)}), 201

@app.route("/surprise-order", methods=["POST"])
def surprise_order():
    available = [p for p in products if p.get("stock", 0) > 0]
    if not available:
        return jsonify({"status": "error", "message": "No products in stock"}), 400
    chosen = random.choice(available)
    payload = request.get_json(silent=True) or {}
    customer_name = (payload.get("customer_name") or "Guest").strip() or "Guest"
    return _create_order_internal(chosen["sku"], customer_name, created_via="surprise")

@app.route("/stats")
def stats():
    total_products = len(products)
    in_stock = sum(1 for p in products if p.get("stock", 0) > 0)
    out_of_stock = total_products - in_stock
    total_orders = len(orders)
    stock_ratio = in_stock / total_products if total_products else 0
    top_rated = None
    best_avg = -1
    for sku, lst in reviews.items():
        if lst:
            avg = sum(r["rating"] for r in lst) / len(lst)
            if avg > best_avg:
                best_avg = avg
                top_rated = {"sku": sku, "avg_rating": round(avg, 2), "reviews": len(lst)}
    return jsonify({
        "products": {"total": total_products, "in_stock": in_stock, "out_of_stock": out_of_stock, "availability_ratio": round(stock_ratio, 2)},
        "orders": {"total": total_orders},
        "top_rated": top_rated
    })

def _create_order():
    data = request.get_json(silent=True) or {}
    sku = (data.get("sku") or "").strip()
    customer_name = (data.get("customer_name") or "").strip()
    if not sku:
        return jsonify({"status": "error", "message": "sku is required"}), 400
    if not customer_name:
        return jsonify({"status": "error", "message": "customer_name is required"}), 400
    return _create_order_internal(sku, customer_name, created_via="standard")

def _create_order_internal(sku, customer_name, created_via):
    global _next_id
    product = next((p for p in products if p.get("sku") == sku), None)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404
    if product.get("stock", 0) <= 0:
        return jsonify({"status": "error", "message": f"{product.get('name', 'Product')} is out of stock"}), 400
    product["stock"] -= 1
    order = {"id": _next_id, "sku": sku, "customer_name": customer_name, "product_name": product["name"], "via": created_via}
    _next_id += 1
    orders.append(order)
    return jsonify({"status": "success", "order": order}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
