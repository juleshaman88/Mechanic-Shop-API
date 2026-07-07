from marshmallow import EXCLUDE, fields

from ...extensions import ma
from ...models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        include_relationships = True

    password = fields.String(load_only=True)
    service_ticket_ids = fields.Method("get_service_ticket_ids", dump_only=True)
    ticket_count = fields.Method("get_ticket_count", dump_only=True)

    def get_service_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.service_tickets]

    def get_ticket_count(self, obj):
        return len(obj.service_tickets)


class MechanicLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        unknown = EXCLUDE
        fields = ("email", "password")

    password = fields.String(required=True, load_only=True)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicLoginSchema()
