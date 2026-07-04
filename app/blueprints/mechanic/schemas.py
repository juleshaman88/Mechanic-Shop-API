from marshmallow import fields

from ...extensions import ma
from ...models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        include_relationships = True

    service_ticket_ids = fields.Method("get_service_ticket_ids", dump_only=True)

    def get_service_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.service_tickets]


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
