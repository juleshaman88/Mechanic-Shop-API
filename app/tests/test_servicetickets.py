import unittest
from datetime import date
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.models import db, ServiceTicket, Customer, Mechanic
from app.utils.utils import encode_mechanic_token
from werkzeug.security import generate_password_hash

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customer(
                name="test user",
                email="test@example.com",
                password=generate_password_hash("password")
            )
            db.session.add(self.customer)
            db.session.commit()
            self.service_ticket = ServiceTicket(
                vin="1HGCM82633A123456",
                service_date=date(2023, 8, 15),
                description="Brake pads replacement",
                status="Pending",
                customer_id=self.customer.id
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            self.mechanic = Mechanic(
                name="John Doe",
                email="johndoe@example.com",
                password="password",
                phone="123-456-7890",
                salary="25.00"
            )
            db.session.add(self.mechanic)
            db.session.commit()
            self.customer_id = self.customer.id
            self.service_ticket_id = self.service_ticket.id
            self.mechanic_id = self.mechanic.id
            self.mechanic_token = encode_mechanic_token(self.mechanic_id)
        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        service_ticket_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2023-08-15",
            "description": "Brake pads replacement",
            "status": "Pending",
            "customer_id": self.customer_id
        }

        response = self.client.post("/service_tickets/", json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["vin"], "1HGCM82633A123456")

    def test_invalid_creation(self):
        service_ticket_payload = {
            "vin": "1HGCM82633A123456",
            "service_date": "2023-08-15",
            "description": "Brake pads replacement",
            "status": "Pending"
        }

        response = self.client.post("/service_tickets/", json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("customer_id", response.json)

    def test_get_service_tickets(self):
        response = self.client.get("/service_tickets/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

    def test_remove_mechanic_from_service_ticket(self):
        self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.mechanic_id}")
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{self.mechanic_id}"
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_remove_mechanic(self):
        invalid_mechanic_id = 9999
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/remove-mechanic/{invalid_mechanic_id}"
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_mechanics_on_service_ticket(self):
        mechanic_payload1 = {
            "name": "John Doe",
            "email": "janedoe@example.com",
            "password": "password",
            "phone": "123-456-7890",
            "salary": "30.00"
        }

        response = self.client.post("/mechanics/", json=mechanic_payload1)
        self.assertEqual(response.status_code, 201)
        mechanic_id1 = response.json["id"]

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/edit",
            json={"add_ids": [mechanic_id1], "remove_ids": []}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(mechanic_id1, response.json["mechanic_ids"])

    def test_add_part_to_ticket(self):
        inventory_payload = {
            "name": "Brake Pads",
            "price": 29.99
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload,
            headers={"Authorization": f"Bearer {self.mechanic_token}"}
        )
        self.assertEqual(response.status_code, 201)
        inventory_id = response.json["id"]

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{inventory_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(inventory_id, response.json["inventory_ids"])

    def test_invalid_add_part_to_ticket(self):
        invalid_inventory_id = 9999
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{invalid_inventory_id}"
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_part_on_ticket(self):
        inventory_payload1 = {
            "name": "Brake Pads",
            "price": 29.99
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload1,
            headers={"Authorization": f"Bearer {self.mechanic_token}"}
        )
        self.assertEqual(response.status_code, 201)
        inventory_id1 = response.json["id"]

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/add-part/{inventory_id1}"
        )
        self.assertEqual(response.status_code, 200)

        inventory_payload2 = {
            "name": "Oil Filter",
            "price": 9.99
        }

        response = self.client.post(
            "/inventory/",
            json=inventory_payload2,
            headers={"Authorization": f"Bearer {self.mechanic_token}"}
        )
        self.assertEqual(response.status_code, 201)
        inventory_id2 = response.json["id"]

        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/edit-parts",
            json={"add_part_ids": [inventory_id2], "remove_part_ids": [inventory_id1]}
        )
        self.assertEqual(response.status_code, 200)
        part_ids = response.json["inventory_ids"]
        self.assertIn(inventory_id2, part_ids)
        self.assertNotIn(inventory_id1, part_ids)

    def test_invalid_edit_part_on_ticket(self):
        invalid_inventory_id = 9999
        response = self.client.put(
            f"/service_tickets/{self.service_ticket_id}/edit-parts",
            json={"add_part_ids": [invalid_inventory_id], "remove_part_ids": []}
        )
        self.assertEqual(response.status_code, 404)

    def test_assign_customer(self):
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-customer/{self.customer_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["customer_id"], self.customer_id)

    def test_invalid_assign_customer(self):
        invalid_customer_id = 9999
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-customer/{invalid_customer_id}")
        self.assertEqual(response.status_code, 404)

    def test_assign_mechanic_to_ticket(self):
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{self.mechanic_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.mechanic_id, response.json["mechanic_ids"])

    def test_invalid_assign_mechanic_to_ticket(self):
        invalid_mechanic_id = 9999
        response = self.client.put(f"/service_tickets/{self.service_ticket_id}/assign-mechanic/{invalid_mechanic_id}")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)