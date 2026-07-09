import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.models import db, Inventory, Mechanic
from app.utils.utils import encode_mechanic_token
from werkzeug.security import generate_password_hash

class TestInventory(unittest.TestCase):
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

            self.inventory_item = Inventory(name="Brake Pads", price=29.99)
            db.session.add(self.inventory_item)
            db.session.commit()

            self.mechanic_id = self.mechanic.id
            self.token = encode_mechanic_token(self.mechanic_id)
            self.inventory_id = self.inventory_item.id
        self.client = self.app.test_client()

    def test_create_inventory_item(self):
        inventory_payload = {
            "name": "Brake Pads",
            "price": "29.99"
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Brake Pads")

    def test_invalid_inventory_creation(self):
        inventory_payload = {
            "name": "Invalid Item"
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.json)
    
    def test_get_inventory_items(self):
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

    def test_get_inventory_item_by_id(self):
        response = self.client.get(f"/inventory/{self.inventory_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json["name"], "Brake Pads")
        self.assertEqual(response.json["price"], 29.99)

    def test_update_inventory_item(self):
        update_payload = {
            "name": "Updated Brake Pads",
            "price": "34.99"
        }

        response = self.client.put(
            f"/inventory/{self.inventory_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Brake Pads")
        self.assertEqual(response.json["price"], 34.99)

    def test_invalid_update_inventory_item(self):
        update_payload = {
            "price": "not-a-number"
        }

        response = self.client.put(
            f"/inventory/{self.inventory_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.json)

    def test_delete_inventory_item(self):
        response = self.client.delete(
            f"/inventory/{self.inventory_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_delete_inventory_item(self):
        response = self.client.delete(
            f"/inventory/{999}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)