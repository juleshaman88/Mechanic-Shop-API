from marshmallow import EXCLUDE, fields

from ...extensions import ma
from ...models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = False
        include_relationships = True
        exclude = ("service_tickets",)
        unknown = EXCLUDE

    password = fields.String(load_only=True, required=True)
    service_ticket_ids = fields.Method("get_service_ticket_ids", dump_only=True)

    def get_service_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.service_tickets]


class LoginSchema(CustomerSchema):
    class Meta(CustomerSchema.Meta):
        exclude = ("id", "name", "service_tickets")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()