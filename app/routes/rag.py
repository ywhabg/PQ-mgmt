from flask import Blueprint, jsonify

bp = Blueprint("rag", __name__, url_prefix="/rag")


@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"module": "rag", "status": "ok"}), 200
