from marshmallow import fields

from ...extensions import ma
from ...models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = False
        include_relationships = True
        exclude = ("mechanics",)

    mechanic_ids = fields.Method("get_mechanic_ids", dump_only=True)

    def get_mechanic_ids(self, obj):
        return [mechanic.id for mechanic in obj.mechanics]


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
