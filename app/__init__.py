from flask import Flask
import config
from .extensions import cache, limiter, ma
from .blueprints.customer import customer_bp
from .blueprints.inventory import inventory_bp
from .models import db
from .blueprints.mechanic import mechanic_bp
from .blueprints.service_ticket import service_ticket_bp


def create_app(config_name="DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(getattr(config, config_name))
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or "dev-secret-key"
    app.config.setdefault("CACHE_TYPE", "SimpleCache")
    app.config.setdefault("RATELIMIT_HEADERS_ENABLED", True)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")

    # INITIALIZE EXTENSIONS
    ma.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    #REGISTER BLUEPRINTS
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service_tickets')

    return app