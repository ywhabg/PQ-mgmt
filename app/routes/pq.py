from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from app import db
from app.models import PQRecord

bp = Blueprint("pq", __name__)

@bp.route("/pq/create", methods=["GET", "POST"])
def create_pq():
    if request.method == "POST":
        pq = PQRecord(
            pq_reference_no=request.form.get("pq_reference_no"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            agency=request.form.get("agency"),
            priority=request.form.get("priority"),
            status="New",
            date_received=datetime.strptime(request.form.get("date_received"), "%Y-%m-%d").date()
        )

        db.session.add(pq)
        db.session.commit()
        return redirect(url_for("pq.list_pq"))

    return render_template("create_pq.html")


@bp.route("/pq")
def list_pq():
    pqs = PQRecord.query.all()
    return render_template("list_pq.html", pqs=pqs)
