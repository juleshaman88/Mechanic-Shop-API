from ...extensions import ma
from ...models import Inventory


class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = False
        include_relationships = True


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)