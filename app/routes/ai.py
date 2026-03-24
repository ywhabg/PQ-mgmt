from flask import Blueprint, jsonify

bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"module": "ai", "status": "ok"}), 200
