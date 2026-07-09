import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.models import db, Mechanic
from app.utils.utils import encode_mechanic_token
from werkzeug.security import generate_password_hash

class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.mechanic = Mechanic(
                name="test user",
                email="test@example.com",
                password=generate_password_hash("password"),
                phone="123-456-7890",
                salary="25.00",
            )
            db.session.add(self.mechanic)
            db.session.commit()
            self.mechanic_id = self.mechanic.id
            self.token = encode_mechanic_token(self.mechanic_id)
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "password": "securepassword",
            "phone": "123-456-7890",
            "salary": "25.00"
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")

    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "Jane Doe",
            "email": "123@gmail.com",
            "salary": "25.00"
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"phone": ["Missing data for required field."]})

    def test_login_mechanic(self):
        mechanic_payload = {
            "email": "test@example.com",
            "password": "password"
        }

        response = self.client.post("/mechanics/login", json=mechanic_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        self.assertEqual(response.json["mechanic"]["email"], "test@example.com")

    def test_invalid_login_mechanic(self):
        mechanic_payload = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }

        response = self.client.post("/mechanics/login", json=mechanic_payload)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Invalid email or password."})

    def test_update_mechanic(self):
        update_payload = {
            "name": "Updated Name",
            "phone": "987-654-3210"
        }

        response = self.client.put(
            f"/mechanics/{self.mechanic_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Name")
        self.assertEqual(response.json["phone"], "987-654-3210")


if __name__ == "__main__":
    unittest.main(verbosity=2)