from flask import Blueprint

bp = Blueprint("pq", __name__, url_prefix="/pq")

@bp.route("/")
def index():
    return "PQ route works"
