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

## Deployment (Render)
1. Create a PostgreSQL database in Render and copy the External Database URL.
2. In your local `.env` file, set:
	- `SQLALCHEMY_DATABASE_URI=<your-render-postgres-uri>`
	- `SECRET_KEY=<your-secret-key>`
3. Confirm `.env` is ignored by git (see `.gitignore`).
4. Ensure your web start command is `gunicorn flask_app:app`.
5. In Render Web Service environment variables, add:
	- `SQLALCHEMY_DATABASE_URI`
	- `SECRET_KEY`
6. Deploy your service from your GitHub repository.
7. After deploy, confirm Swagger uses your live host and HTTPS:
	- Host: `mechanic-shop-api-4ig7.onrender.com`
	- Scheme: `https`

## Local Run (Windows PowerShell)
1. Activate virtual environment:
```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .\.venv\Scripts\Activate.ps1)
```

2. Install dependencies:
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Run tests:
```powershell
python -m unittest discover -s app/tests -p "test_*.py" -v
```

4. Run API locally (testing config):
```powershell
$env:FLASK_CONFIG='TestingConfig'
python -m flask --app flask_app run --port 5050
```

5. Open:
	- API: `http://127.0.0.1:5050/customers/`
	- Swagger UI: `http://127.0.0.1:5050/api/docs/`

## CI/CD Pipeline (GitHub Actions)
Workflow file: `.github/workflows/main.yaml`

This workflow includes:
1. `build` job: installs dependencies and verifies app import.
2. `test` job: runs unittest suite (`python -m unittest discover -s app/tests -p "test_*.py" -v`).
3. `deploy` job: triggers Render deploy only after tests pass (`needs: test`) and only on pushes to `main`.

### Required GitHub Repository Secrets
Add the following secret in your GitHub repository settings:
- `RENDER_DEPLOY_HOOK_URL` = your Render deploy hook URL

## Security Note
- If a deploy hook URL is ever exposed publicly, rotate/regenerate it in Render and update the GitHub secret immediately.