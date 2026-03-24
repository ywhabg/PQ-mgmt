from flask import Blueprint, jsonify

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"module": "dashboard", "status": "ok"}), 200
