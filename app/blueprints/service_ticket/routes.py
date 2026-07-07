from flask import jsonify, request
from marshmallow import ValidationError

from ...extensions import cache
from ...models import Inventory, Mechanic, ServiceTicket, db
from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_ticket_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    service_ticket = ServiceTicket(**service_ticket_data)

    db.session.add(service_ticket)
    db.session.commit()
    cache.clear()
    return service_ticket_schema.jsonify(service_ticket), 201


@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if mechanic is None:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this ticket."}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if mechanic is None:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic is not assigned to this ticket."}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def edit_mechanics_on_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    payload = request.get_json() or {}
    add_ids = payload.get("add_ids", [])
    remove_ids = payload.get("remove_ids", [])

    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic is None:
            return jsonify({"error": f"Mechanic {mechanic_id} not found."}), 404
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic is None:
            return jsonify({"error": f"Mechanic {mechanic_id} not found."}), 404
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:inventory_id>", methods=["PUT"])
def add_part_to_ticket(ticket_id, inventory_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    part = db.session.get(Inventory, inventory_id)
    if part is None:
        return jsonify({"error": "Inventory item not found."}), 404

    if part not in ticket.inventory:
        ticket.inventory.append(part)

    db.session.commit()
    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/", methods=["GET"])
@cache.cached(timeout=180)
def get_service_tickets():
    tickets = db.session.query(ServiceTicket).all()
    return service_tickets_schema.jsonify(tickets), 200
