A mechanic shop dashboard integrated with API, caching, limiters, advanced queries, and JSON. This RESTful API invokes all CRUD fundamental operations.

This app takes advantage of Token Authentication for the following blueprints: 
- Customer
- Mechanic

With proper Token Authentication, the following items are limited to viewing based on authorization: 
- Service Tickets on the Mechanic side as well as Customer side

Postman collection includes all APIs invoked on the following blueprints: 
- Customer
- Inventory
- Mechanic
- Service Ticket

## Requirements to Run this App Successfully: 
Flask
Flask-Caching
Flask-Limiter
Flask-Marshmallow
Flask-SQLAlchemy
marshmallow
mysql-connector-python
python-jose