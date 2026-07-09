A mechanic shop dashboard integrated with API, caching, limiters, advanced queries, Swagger UI, and advanced unit testing. This RESTful API invokes all CRUD fundamental operations.

This app takes advantage of Token Authentication for the following blueprints: 
- Customer
- Mechanic

With proper Token Authentication, the following items are limited to view and/or update based on authorization: 
- Service Tickets view for customers
- Updating of Mechanic information
- Deletion of Mechanics
- Creation of Inventory items
- Update of Inventory items
- Deletion of Inventory items

Postman collection includes all APIs endpoints invoked on the following blueprints: 
- Customer
- Inventory
- Mechanic
- Service Ticket

Swaagger UI includes sample test runs for all endpoints in each blueprint following CRUD operations. 

Each endpoint has tests created in the tests folder, with inclusion of accurate submissions as well as invalid submissions to ensure error handling was done appropriately. 

## Requirements to Run this App Successfully: 
Flask
Flask-Caching
Flask-Limiter
Flask-Marshmallow
Flask-SQLAlchemy
marshmallow
mysql-connector-python
python-jose