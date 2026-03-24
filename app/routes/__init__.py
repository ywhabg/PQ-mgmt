from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"module": "auth", "status": "ok"}), 200


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Demo login only
    token = create_access_token(identity=email)

    return jsonify(
        {
            "message": "Login successful",
            "access_token": token,
        }
    ), 200
