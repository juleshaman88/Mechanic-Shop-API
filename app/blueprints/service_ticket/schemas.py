from marshmallow import fields

from ...extensions import ma
from ...models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = False
        include_relationships = True
        exclude = ("mechanics", "inventory", "customer")

    mechanic_ids = fields.Method("get_mechanic_ids", dump_only=True)
    inventory_ids = fields.Method("get_inventory_ids", dump_only=True)
    customer_id = fields.Integer(required=True)

    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]

    def get_inventory_ids(self, obj):
        return [inventory.id for inventory in obj.inventory]


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
