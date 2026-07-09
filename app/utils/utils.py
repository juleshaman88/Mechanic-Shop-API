import os

from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import current_app, jsonify, request
from jose import JWTError, jwt

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"

def encode_token(customer_id):
    payload = {
        "token_type": "customer",
        "customer_id": customer_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def encode_mechanic_token(mechanic_id):
    payload = {
        "token_type": "mechanic",
        "mechanic_id": mechanic_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Bearer token required."}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            decoded_token = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            if decoded_token.get("token_type") != "customer":
                return jsonify({"error": "Customer token required."}), 401
            customer_id = decoded_token.get("customer_id")
        except JWTError:
            return jsonify({"error": "Invalid or expired token."}), 401

        if customer_id is None:
            return jsonify({"error": "Token is missing customer information."}), 401

        return function(customer_id, *args, **kwargs)

    return decorated


def mechanic_token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Bearer token required."}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            decoded_token = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            if decoded_token.get("token_type") != "mechanic":
                return jsonify({"error": "Mechanic token required."}), 401
            mechanic_id = decoded_token.get("mechanic_id")
        except JWTError:
            return jsonify({"error": "Invalid or expired token."}), 401

        if mechanic_id is None:
            return jsonify({"error": "Token is missing mechanic information."}), 401

        return function(mechanic_id, *args, **kwargs)

    return decorated