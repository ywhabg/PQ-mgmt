from flask import Blueprint, jsonify

bp = Blueprint("workflow", __name__, url_prefix="/workflow")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"module": "workflow", "status": "ok"}), 200
