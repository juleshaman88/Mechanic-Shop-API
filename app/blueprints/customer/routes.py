from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from ...extensions import limiter, cache
from ...models import Customer, ServiceTicket, db
from ...utils.utils import encode_token, token_required
from . import customer_bp
from .schemas import customer_schema, customers_schema, login_schema
from ..service_ticket.schemas import service_tickets_schema


@customer_bp.route("/", methods=["POST"])
@limiter.limit("25 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    customer_data["password"] = generate_password_hash(customer_data["password"])
    customer = Customer(**customer_data)

    db.session.add(customer)
    db.session.commit()
    return customer_schema.jsonify(customer), 201


@customer_bp.route("/login", methods=["POST"])
@limiter.limit("25 per half hour")
def login_customer():
    try:
        login_data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    customer = db.session.query(Customer).filter_by(email=login_data["email"]).first()
    if customer is None or not check_password_hash(customer.password, login_data["password"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token, "customer": customer_schema.dump(customer)}), 200


@customer_bp.route("/", methods=["GET"])
def get_customers():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers.items), 200
    
    except:
        query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200


@customer_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):
    try:
        tickets = db.session.query(ServiceTicket).filter_by(customer_id=customer_id).all()
        return jsonify({"customer_id": customer_id, "service_tickets": service_tickets_schema.dump(tickets)}), 200
    except:
        return jsonify({"error": "Failed to retrieve service tickets."}), 500