from flask import jsonify, request
from sqlalchemy import select
from marshmallow import ValidationError

from ...extensions import cache
from ...models import Inventory, db
from ...utils.utils import mechanic_token_required
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
def get_inventory_items():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(Inventory)
        inventory_items = db.session.execute(query).scalars().paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
        return inventories_schema.jsonify(inventory_items.items), 200
    
    except:
        query = select(Inventory)
        inventory_items = db.session.execute(query).scalars().all()
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