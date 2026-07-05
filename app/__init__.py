from flask import Flask
import config
from .extensions import ma
from .models import db
from .blueprints.mechanic import mechanic_bp
from .blueprints.service_ticket import service_ticket_bp


def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(getattr(config, config_name))

    # INITIALIZE EXTENSIONS
    ma.init_app(app)
    db.init_app(app)

    #REGISTER BLUEPRINTS
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service_tickets')

    return app