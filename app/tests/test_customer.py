import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.models import db, Customer
from app.utils.utils import encode_token
from werkzeug.security import generate_password_hash

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customer(
                name="test user",
                email="test@example.com",
                password=generate_password_hash("password"),
            )
            db.session.add(self.customer)
            db.session.commit()
            self.customer_id = self.customer.id
            self.customer_token = encode_token(self.customer_id)
        self.client = self.app.test_client()

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "password": "securepassword",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")

    def test_invalid_creation(self):
        customer_payload = {
            "name": "Jane Doe",
            "email": "123@gmail.com",
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"password": ["Missing data for required field."]})

    def test_login_customer(self):
        customer_payload = {
            "email": "test@example.com",
            "password": "password"
        }

        response = self.client.post("/customers/login", json=customer_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        self.assertEqual(response.json["customer"]["email"], "test@example.com")

    def test_invalid_login_customer(self):
        customer_payload = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }

        response = self.client.post("/customers/login", json=customer_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Invalid email or password."})

    def test_get_customers(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

    def test_get_my_tickets(self):
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.get(
            f"/customers/my-tickets",
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json["customer_id"], self.customer_id)
        self.assertIn("service_tickets", response.json)
        self.assertIsInstance(response.json["service_tickets"], list)


if __name__ == "__main__":
    unittest.main(verbosity=2)