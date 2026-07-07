from flask import jsonify, request
from marshmallow import ValidationError

from ...extensions import cache
from ...models import Inventory, db
from ...utils import mechanic_token_required
from . import inventory_bp
from .schemas import inventories_schema, inventory_schema


@inventory_bp.route("/", methods=["POST"])
@mechanic_token_required
def create_inventory_item(mechanic_id):
    try:
        inventory_data = inventory_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    inventory_item = Inventory(**inventory_data)
    db.session.add(inventory_item)
    db.session.commit()
    cache.clear()
    return inventory_schema.jsonify(inventory_item), 201


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=120)
def get_inventory_items():
    inventory_items = db.session.query(Inventory).order_by(Inventory.id).all()
    return inventories_schema.jsonify(inventory_items), 200


@inventory_bp.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    if inventory_item is None:
        return jsonify({"error": "Inventory item not found."}), 404

    return inventory_schema.jsonify(inventory_item), 200


@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
@mechanic_token_required
def update_inventory_item(mechanic_id, inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    if inventory_item is None:
        return jsonify({"error": "Inventory item not found."}), 404

    try:
        updated_data = inventory_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in updated_data.items():
        setattr(inventory_item, key, value)

    db.session.commit()
    cache.clear()
    return inventory_schema.jsonify(inventory_item), 200


@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
@mechanic_token_required
def delete_inventory_item(mechanic_id, inventory_id):
    inventory_item = db.session.get(Inventory, inventory_id)
    if inventory_item is None:
        return jsonify({"error": "Inventory item not found."}), 404

    db.session.delete(inventory_item)
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Inventory item {inventory_id} deleted."}), 200