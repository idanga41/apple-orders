# test_orders.py
import unittest
import json
from app import app  # מייבא את אובייקט ה-Flask מהפרויקט שלך


class TestAppleOrdersAPI(unittest.TestCase):
    """בדיקות יחידה ל-Apple Orders API"""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # ---------- GET /products ----------
    def test_get_products_returns_list(self):
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200, "GET /products אמור להחזיר 200")
        data = resp.get_json()
        self.assertIsInstance(data, list, "GET /products אמור להחזיר רשימה")
        # אם יש מוצרים, נבדוק שלכל פריט יש לפחות שדה sku
        if data:
            self.assertIn("sku", data[0], "פריט מוצר צריך לכלול sku")

    # ---------- POST /order (happy path) ----------
    def test_post_order_valid_sku_decrements_stock(self):
        # 1) נקבל את רשימת המוצרים ונבחר SKU ראשון
        products_before = self.client.get("/products").get_json()
        self.assertIsInstance(products_before, list)
        self.assertGreater(len(products_before), 0, "אמור להיות לפחות מוצר אחד לבדיקת הזמנה")

        first = products_before[0]
        sku = first.get("sku")
        self.assertIsNotNone(sku, "למוצר צריך להיות שדה sku")
        # ננסה לקרוא גם את ה-stock אם קיים כדי לבדוק ירידה
        stock_before = first.get("stock")

        # 2) נבצע הזמנה תקינה
        order_payload = {"sku": sku, "customer_name": "Test User"}
        resp_order = self.client.post(
            "/order",
            data=json.dumps(order_payload),
            content_type="application/json",
        )
        # לא ננעל על קוד ספציפי (200/201/202), אבל נצפה ל-2xx
        self.assertTrue(
            200 <= resp_order.status_code < 300,
            f"POST /order על sku קיים אמור להחזיר 2xx, קיבלנו {resp_order.status_code}",
        )

        # 3) נבדוק שהמלאי ירד (אם השרת חושף stock)
        products_after = self.client.get("/products").get_json()
        # נמצא שוב את אותו מוצר
        same_after = next((p for p in products_after if p.get("sku") == sku), None)
        self.assertIsNotNone(same_after, "המוצר שהוזמן צריך עדיין להופיע ברשימת /products")
        if stock_before is not None and same_after.get("stock") is not None:
            self.assertEqual(
                same_after["stock"], stock_before - 1,
                "הזמנה אמורה להוריד את ה-stock ב-1"
            )

    # ---------- POST /order (body לא תקין) ----------
    def test_post_order_missing_sku_returns_400(self):
        bad_payload = {"customer_name": "No SKU"}
        resp = self.client.post("/order", data=json.dumps(bad_payload),
                                content_type="application/json")
        # אם המימוש שלך מחזיר 400 לבקשה חסרה — הבדיקה תעבור.
        # אם בחרת קוד אחר (422/404), עדכן כאן בהתאם.
        self.assertIn(
            resp.status_code, [400, 422],
            f"ציפינו לשגיאה בקלט חסר (400/422), קיבלנו {resp.status_code}"
        )

    # ---------- POST /order (SKU לא קיים) ----------
    def test_post_order_unknown_sku_returns_404_or_400(self):
        payload = {"sku": "NON-EXISTENT-SKU-XYZ", "customer_name": "Ghost"}
        resp = self.client.post("/order", data=json.dumps(payload),
                                content_type="application/json")
        # נחשב תקין אם השרת מחזיר 404 (מוצר לא נמצא) או 400/422 (קלט לא תקין)
        self.assertIn(
            resp.status_code, [404, 400, 422],
            f"ציפינו לשגיאה עבור SKU לא קיים (404/400/422), קיבלנו {resp.status_code}"
        )


if __name__ == "__main__":
    unittest.main()
