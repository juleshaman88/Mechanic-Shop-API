from app import create_app
from app.extensions import db
from flask import Flask

app = create_app('DevelopmentConfig')

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()