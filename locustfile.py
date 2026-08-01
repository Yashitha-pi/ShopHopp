"""
locustfile.py
---------------
Starter load test for the shopping app API. Run with:

    pip install locust
    locust -f locustfile.py --host=http://127.0.0.1:5000

Then open http://localhost:8089 to configure users/spawn-rate and start
the test. This is what will later feed real "concurrent users" /
"request rate" numbers into the MLOps resource-prediction dataset.
"""

import random
from locust import HttpUser, task, between


class ShopperUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Each simulated user registers its own account once, then logs in."""
        suffix = random.randint(1, 10_000_000)
        self.email = f"loadtest{suffix}@example.com"
        self.password = "password123"

        self.client.post("/api/register", json={
            "name": f"Load Test {suffix}",
            "email": self.email,
            "password": self.password,
        })

    @task(4)
    def browse_products(self):
        self.client.get("/api/products")

    @task(2)
    def search_products(self):
        self.client.get("/api/products?search=shoe")

    @task(2)
    def view_categories(self):
        self.client.get("/api/categories")

    @task(2)
    def add_to_cart(self):
        # Product IDs 1-8 exist in the seeded demo dataset.
        product_id = random.randint(1, 8)
        self.client.post("/api/cart/add", json={"product_id": product_id, "quantity": 1})

    @task(1)
    def view_cart(self):
        self.client.get("/api/cart")

    @task(1)
    def checkout(self):
        self.client.post("/api/checkout")
