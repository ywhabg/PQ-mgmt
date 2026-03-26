from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.forms import PQForm, PQUpdateForm
from app.models import PQRecord, PQUpdate, User

pq_bp = Blueprint("pq", __name__, url_prefix="/pq")


@pq_bp.route("/")
@login_required
def list_pqs():
    status = request.args.get("status", "").strip()
    agency = request.args.get("agency", "").strip()
    keyword = request.args.get("keyword", "").strip()

    query = PQRecord.query

    if status:
        query = query.filter(PQRecord.status == status)

    if agency:
        query = query.filter(PQRecord.ministry_or_agency.ilike(f"%{agency}%"))

    if keyword:
        query = query.filter(
            (PQRecord.pq_reference_no.ilike(f"%{keyword}%")) |
            (PQRecord.title.ilike(f"%{keyword}%"))
        )

    pqs = query.order_by(PQRecord.created_at.desc()).all()

    return render_template("pq_list.html", pqs=pqs, status=status, agency=agency, keyword=keyword)


@pq_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_pq():
    form = PQForm()
    users = User.query.filter_by(is_active_user=True).order_by(User.full_name.asc()).all()
    form.assigned_to_user_id.choices = [(0, "-- Unassigned --")] + [(u.id, u.full_name) for u in users]

    if form.validate_on_submit():
        pq = PQRecord(
            pq_reference_no=form.pq_reference_no.data.strip(),
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            ministry_or_agency=form.ministry_or_agency.data.strip(),
            submitted_by=form.submitted_by.data.strip(),
            assigned_to_user_id=form.assigned_to_user_id.data if form.assigned_to_user_id.data != 0 else None,
            priority=form.priority.data,
            status=form.status.data,
            due_date=form.due_date.data,
            date_received=form.date_received.data,
        )

        db.session.add(pq)
        db.session.commit()

        initial_update = PQUpdate(
            pq_id=pq.id,
            update_text="PQ record created.",
            update_type="General",
            updated_by_user_id=current_user.id
        )
        db.session.add(initial_update)
        db.session.commit()

        flash("PQ created successfully.", "success")
        return redirect(url_for("pq.view_pq", pq_id=pq.id))

    return render_template("pq_create.html", form=form)


@pq_bp.route("/<int:pq_id>", methods=["GET", "POST"])
@login_required
def view_pq(pq_id):
    pq = PQRecord.query.get_or_404(pq_id)
    update_form = PQUpdateForm()

    if update_form.validate_on_submit():
        update = PQUpdate(
            pq_id=pq.id,
            update_text=update_form.update_text.data.strip(),
            update_type=update_form.update_type.data,
            updated_by_user_id=current_user.id
        )
        db.session.add(update)
        db.session.commit()

        flash("Update added successfully.", "success")
        return redirect(url_for("pq.view_pq", pq_id=pq.id))

    return render_template("pq_detail.html", pq=pq, update_form=update_form)


@pq_bp.route("/<int:pq_id>/edit", methods=["GET", "POST"])
@login_required
def edit_pq(pq_id):
    pq = PQRecord.query.get_or_404(pq_id)
    form = PQForm(obj=pq)

    users = User.query.filter_by(is_active_user=True).order_by(User.full_name.asc()).all()
    form.assigned_to_user_id.choices = [(0, "-- Unassigned --")] + [(u.id, u.full_name) for u in users]
    form.assigned_to_user_id.data = pq.assigned_to_user_id or 0

    if form.validate_on_submit():
        old_status = pq.status
        old_assignee = pq.assigned_to_user_id

        pq.pq_reference_no = form.pq_reference_no.data.strip()
        pq.title = form.title.data.strip()
        pq.description = form.description.data.strip()
        pq.ministry_or_agency = form.ministry_or_agency.data.strip()
        pq.submitted_by = form.submitted_by.data.strip()
        pq.assigned_to_user_id = form.assigned_to_user_id.data if form.assigned_to_user_id.data != 0 else None
        pq.priority = form.priority.data
        pq.status = form.status.data
        pq.due_date = form.due_date.data
        pq.date_received = form.date_received.data

        if pq.status == "Closed" and not pq.date_closed:
            pq.date_closed = date.today()
        elif pq.status != "Closed":
            pq.date_closed = None

        db.session.commit()

        if old_status != pq.status:
            db.session.add(PQUpdate(
                pq_id=pq.id,
                update_text=f"Status changed from '{old_status}' to '{pq.status}'.",
                update_type="Status Change",
                updated_by_user_id=current_user.id
            ))

        if old_assignee != pq.assigned_to_user_id:
            db.session.add(PQUpdate(
                pq_id=pq.id,
                update_text="Assignment updated.",
                update_type="Assignment",
                updated_by_user_id=current_user.id
            ))

        db.session.commit()

        flash("PQ updated successfully.", "success")
        return redirect(url_for("pq.view_pq", pq_id=pq.id))

    return render_template("pq_create.html", form=form, is_edit=True, pq=pq)
