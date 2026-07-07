from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from ...extensions import cache, limiter
from ...models import db, Mechanic, ServiceTicket
from ...utils import encode_mechanic_token, mechanic_token_required
from . import mechanic_bp
from .schemas import mechanic_login_schema, mechanic_schema, mechanics_schema


@mechanic_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    existing_mechanic = db.session.query(Mechanic).filter_by(email=mechanic_data["email"]).first()
    if existing_mechanic is not None:
        return jsonify({"error": "A mechanic with that email already exists."}), 409

    if not mechanic_data.get("password"):
        mechanic_data["password"] = generate_password_hash(mechanic_data["email"])
    else:
        mechanic_data["password"] = generate_password_hash(mechanic_data["password"])

    mechanic = Mechanic(**mechanic_data)

    db.session.add(mechanic)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A mechanic with that email already exists."}), 409

    cache.clear()
    return mechanic_schema.jsonify(mechanic), 201


@mechanic_bp.route("/", methods=["GET"])
@cache.cached(timeout=60)
def get_mechanics():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = db.session.query(Mechanic).order_by(Mechanic.id).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    mechanics = pagination.items
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/login", methods=["POST"])
@limiter.limit("5 per half hour")
def login_mechanic():
    try:
        login_data = mechanic_login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    mechanic = db.session.query(Mechanic).filter_by(email=login_data["email"]).first()
    if mechanic is None or not mechanic.password:
        return jsonify({"error": "Invalid email or password."}), 401

    if not check_password_hash(mechanic.password, login_data["password"]):
        return jsonify({"error": "Invalid email or password."}), 401

    token = encode_mechanic_token(mechanic.id)
    return jsonify({"token": token, "mechanic": mechanic_schema.dump(mechanic)}), 200


@mechanic_bp.route("/ranked", methods=["GET"])
def get_mechanics_ranked_by_tickets():
    mechanics = (
        db.session.query(Mechanic)
        .outerjoin(Mechanic.service_tickets)
        .group_by(Mechanic.id)
        .order_by(func.count(ServiceTicket.id).desc(), Mechanic.id.asc())
        .all()
    )
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/<int:id>", methods=["PUT"])
@mechanic_token_required
def update_mechanic(mechanic_id, id):
    mechanic = db.session.get(Mechanic, id)
    if mechanic is None:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        updated_data = mechanic_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in updated_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    cache.clear()
    return mechanic_schema.jsonify(mechanic), 200


@mechanic_bp.route("/<int:id>", methods=["DELETE"])
@limiter.limit("2 per hour")
@mechanic_token_required
def delete_mechanic(mechanic_id, id):
    mechanic = db.session.get(Mechanic, id)
    if mechanic is None:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Mechanic {id} deleted."}), 200
