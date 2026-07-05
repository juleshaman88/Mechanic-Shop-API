import os

from app import create_app
from app.models import db
from flask import Flask

app = create_app('DevelopmentConfig')

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))