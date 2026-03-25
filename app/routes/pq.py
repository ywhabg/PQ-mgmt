from flask import Blueprint, render_template, request, redirect, url_for
from app.models import PQRecord
from app import db
from datetime import datetime

pq_bp = Blueprint('pq', __name__)

@pq_bp.route("/pq/create", methods=["GET", "POST"])
def create_pq():
    
    if request.method == "POST":
        pq = PQRecord(
            pq_reference_no=request.form.get("pq_reference_no"),
            title=request.form.get("title"),
            description=request.form.get("description"),
            agency=request.form.get("agency"),
            priority=request.form.get("priority"),
            status="New",
            date_received=datetime.strptime(
                request.form.get("date_received"), "%Y-%m-%d"
            )
        )

        db.session.add(pq)
        db.session.commit()

        return redirect(url_for("pq.list_pq"))

    # 👇 THIS IS WHERE IT BELONGS
    return render_template("create_pq.html")
