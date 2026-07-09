import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.models import db, Customer
from app.utils.utils import encode_customer_token
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
                phone="123-456-7890",
            )
            db.session.add(self.customer)
            db.session.commit()
            self.customer_id = self.customer.id
            self.token = encode_customer_token(self.customer_id)
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
            "password": "securepassword"
        }

        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"phone": ["Missing data for required field."]})

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

    def test_update_customer(self):
        update_payload = {
            "name": "Updated Name",
            "phone": "987-654-3210"
        }

        response = self.client.put(
            f"/customers/{self.customer_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Name")
        self.assertEqual(response.json["phone"], "987-654-3210")


if __name__ == "__main__":
    unittest.main(verbosity=2)