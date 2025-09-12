# test_orders.py
import unittest
import json
import app as appmod

app = appmod.app


def _reset_state():
    """Reset in-memory state so tests are deterministic."""
    if hasattr(appmod, "orders"):
        appmod.orders.clear()
    if hasattr(appmod, "reviews"):
        appmod.reviews.clear()
    if hasattr(appmod, "_next_id"):
        appmod._next_id = 1
    sku_defaults = {
        "APL-IPH15-256-BLK": 5,
        "APL-IPAD-AIR-128-BLU": 3,
        "APL-MBP-14-1TB-SLV": 0,
    }
    if hasattr(appmod, "products"):
        for p in appmod.products:
            sku = p.get("sku")
            if sku in sku_defaults:
                p["stock"] = sku_defaults[sku]


class TestAppleOrdersAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        _reset_state()

    def test_health_ok(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)
        self.assertEqual(resp.get_json().get("status"), "ok")

    def test_get_products_returns_list(self):
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("sku", data[0])

    def test_post_order_valid_sku_decrements_stock(self):
        products_before = self.client.get("/products").get_json()
        self.assertGreater(len(products_before), 0)
        sku = products_before[0]["sku"]
        stock_before = products_before[0].get("stock")

        payload = {"sku": sku, "customer_name": "Test User"}
        resp = self.client.post("/order", data=json.dumps(payload), content_type="application/json")
        self.assertTrue(200 <= resp.status_code < 300, f"Expected 2xx, got {resp.status_code}")

        products_after = self.client.get("/products").get_json()
        same_after = next((p for p in products_after if p.get("sku") == sku), None)
        self.assertIsNotNone(same_after)
        if stock_before is not None and same_after.get("stock") is not None:
            self.assertEqual(same_after["stock"], stock_before - 1)

    def test_post_order_missing_sku_returns_4xx(self):
        bad_payload = {"customer_name": "No SKU"}
        resp = self.client.post("/order", data=json.dumps(bad_payload), content_type="application/json")
        self.assertIn(resp.status_code, [400, 422])

    def test_post_order_unknown_sku_returns_404_or_4xx(self):
        payload = {"sku": "NON-EXISTENT-SKU-XYZ", "customer_name": "Ghost"}
        resp = self.client.post("/order", data=json.dumps(payload), content_type="application/json")
        self.assertIn(resp.status_code, [404, 400, 422])

    def test_orders_flow_create_list_get(self):
        sku = "APL-IPH15-256-BLK"
        create = self.client.post("/orders", json={"sku": sku, "customer_name": "Alma"})
        self.assertEqual(create.status_code, 201)
        body = create.get_json()
        self.assertEqual(body["status"], "success")
        oid = body["order"]["id"]

        lst = self.client.get("/orders")
        self.assertEqual(lst.status_code, 200)
        items = lst.get_json()
        self.assertTrue(any(o.get("id") == oid for o in items))

        single = self.client.get(f"/orders/{oid}")
        self.assertEqual(single.status_code, 200)
        self.assertEqual(single.get_json().get("id"), oid)

    def test_reviews_add_and_get(self):
        sku = "APL-IPH15-256-BLK"
        add = self.client.post(f"/products/{sku}/reviews", json={"rating": 5, "comment": "Great"})
        self.assertEqual(add.status_code, 201)

        get = self.client.get(f"/products/{sku}/reviews")
        self.assertEqual(get.status_code, 200)
        data = get.get_json()
        self.assertEqual(data["sku"], sku)
        self.assertEqual(data["count"], 1)
        self.assertAlmostEqual(float(data["avg_rating"]), 5.0, places=2)

    def test_surprise_order_reduces_stock(self):
        before = {p["sku"]: p["stock"] for p in appmod.products}
        resp = self.client.post("/surprise-order", json={"customer_name": "Eli"})
        self.assertEqual(resp.status_code, 201)

        body = resp.get_json()
        self.assertEqual(body["status"], "success")
        chosen_sku = body["order"]["sku"]

        after = {p["sku"]: p["stock"] for p in appmod.products}
        self.assertIn(chosen_sku, before)
        self.assertEqual(after[chosen_sku], before[chosen_sku] - 1)
        self.assertEqual(len(appmod.orders), 1)

    def test_stats_endpoint(self):
        self.client.post("/products/APL-IPH15-256-BLK/reviews", json={"rating": 4})
        self.client.post("/orders", json={"sku": "APL-IPH15-256-BLK", "customer_name": "U1"})

        resp = self.client.get("/stats")
        self.assertEqual(resp.status_code, 200)
        s = resp.get_json()
        self.assertIn("products", s)
        self.assertIn("orders", s)
        self.assertGreaterEqual(s["products"]["total"], 1)
        self.assertEqual(s["orders"]["total"], 1)
        self.assertIsNotNone(s.get("top_rated"))


if __name__ == "__main__":
    unittest.main()
