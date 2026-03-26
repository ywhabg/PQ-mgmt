from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required

from app.models import PQRecord

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    total_pqs = PQRecord.query.count()
    open_pqs = PQRecord.query.filter(PQRecord.status != "Closed").count()
    closed_pqs = PQRecord.query.filter_by(status="Closed").count()
    overdue_pqs = PQRecord.query.filter(
        PQRecord.due_date.isnot(None),
        PQRecord.due_date < date.today(),
        PQRecord.status != "Closed"
    ).count()

    recent_pqs = PQRecord.query.order_by(PQRecord.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_pqs=total_pqs,
        open_pqs=open_pqs,
        closed_pqs=closed_pqs,
        overdue_pqs=overdue_pqs,
        recent_pqs=recent_pqs
    )
