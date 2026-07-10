from flask import jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...extensions import cache, limiter
from ...models import Customer, Inventory, Mechanic, ServiceTicket, db
from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_ticket_bp.route("/", methods=["POST"])
@limiter.limit("25 per hour")
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    service_ticket = ServiceTicket(**service_ticket_data)

    db.session.add(service_ticket)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to create service ticket."}), 500

    cache.clear()
    return service_ticket_schema.jsonify(service_ticket), 201


@service_ticket_bp.route("/", methods=["GET"])
def get_service_tickets():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(ServiceTicket)
        service_tickets = db.paginate(query, page=page, per_page=per_page)
        return service_tickets_schema.jsonify(service_tickets.items), 200
    
    except:
        query = select(ServiceTicket)
        service_tickets = db.session.execute(query).scalars().all()
        return service_tickets_schema.jsonify(service_tickets), 200


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
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

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

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

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

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/edit-parts", methods=["PUT"])
def edit_parts_on_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    payload = request.get_json() or {}
    add_part_ids = payload.get("add_part_ids", [])
    remove_part_ids = payload.get("remove_part_ids", [])

    for inventory_id in add_part_ids:
        part = db.session.get(Inventory, inventory_id)
        if part is None:
            return jsonify({"error": f"Inventory item {inventory_id} not found."}), 404
        if part not in ticket.inventory:
            ticket.inventory.append(part)

    for inventory_id in remove_part_ids:
        part = db.session.get(Inventory, inventory_id)
        if part is None:
            return jsonify({"error": f"Inventory item {inventory_id} not found."}), 404
        if part in ticket.inventory:
            ticket.inventory.remove(part)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/assign-customer/<int:customer_id>", methods=["PUT"])
def assign_customer(ticket_id, customer_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if ticket is None:
        return jsonify({"error": "Service ticket not found."}), 404

    customer = db.session.get(Customer, customer_id)
    if customer is None:
        return jsonify({"error": "Customer not found."}), 404

    ticket.customer_id = customer.id
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200
    

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
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Failed to update service ticket."}), 500

    cache.clear()
    return service_ticket_schema.jsonify(ticket), 200