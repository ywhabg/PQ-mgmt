from datetime import date

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms import PQForm, PQUpdateForm
from app.models import PQRecord, PQUpdate, User

pq_bp = Blueprint("pq", __name__, url_prefix="/pq")


def get_active_user_choices():
    """
    Build dropdown choices safely.
    Falls back to email or user id if full_name is missing.
    """
    users = User.query.filter_by(is_active_user=True).all()

    def user_label(user):
        return (
            getattr(user, "full_name", None)
            or getattr(user, "email", None)
            or getattr(user, "username", None)
            or f"User {user.id}"
        )

    users = sorted(users, key=lambda u: user_label(u).lower())
    return [(0, "-- Unassigned --")] + [(u.id, user_label(u)) for u in users]


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
        like_term = f"%{keyword}%"
        query = query.filter(
            or_(
                PQRecord.pq_reference_no.ilike(like_term),
                PQRecord.title.ilike(like_term),
                PQRecord.description.ilike(like_term),
                PQRecord.ministry_or_agency.ilike(like_term),
                PQRecord.submitted_by.ilike(like_term),
            )
        )

    pqs = query.order_by(PQRecord.created_at.desc()).all()

    return render_template(
        "pq_list.html",
        pqs=pqs,
        status=status,
        agency=agency,
        keyword=keyword,
    )


@pq_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_pq():
    form = PQForm()
    form.assigned_to_user_id.choices = get_active_user_choices()

    if form.validate_on_submit():
        try:
            pq = PQRecord(
                pq_reference_no=form.pq_reference_no.data.strip(),
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                ministry_or_agency=form.ministry_or_agency.data.strip(),
                submitted_by=form.submitted_by.data.strip(),
                assigned_to_user_id=(
                    None if form.assigned_to_user_id.data == 0 else form.assigned_to_user_id.data
                ),
                priority=form.priority.data,
                status=form.status.data,
                due_date=form.due_date.data,
                date_received=form.date_received.data,
            )

            db.session.add(pq)
            db.session.flush()

            initial_update = PQUpdate(
                pq_id=pq.id,
                update_text="PQ record created.",
                update_type="General",
                updated_by_user_id=current_user.id,
            )
            db.session.add(initial_update)

            db.session.commit()

            flash("PQ created successfully.", "success")
            return redirect(url_for("pq.view_pq", pq_id=pq.id))

        except IntegrityError:
            db.session.rollback()
            flash("PQ reference number already exists.", "danger")

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating PQ: {str(e)}", "danger")

    elif request.method == "POST":
        flash(f"Form validation failed: {form.errors}", "danger")

    return render_template("pq_create.html", form=form, is_edit=False)


@pq_bp.route("/<int:pq_id>", methods=["GET", "POST"])
@login_required
def view_pq(pq_id):
    pq = PQRecord.query.get_or_404(pq_id)
    update_form = PQUpdateForm()

    if update_form.validate_on_submit():
        try:
            update = PQUpdate(
                pq_id=pq.id,
                update_text=update_form.update_text.data.strip(),
                update_type=update_form.update_type.data,
                updated_by_user_id=current_user.id,
            )
            db.session.add(update)
            db.session.commit()

            flash("Update added successfully.", "success")
            return redirect(url_for("pq.view_pq", pq_id=pq.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding update: {str(e)}", "danger")

    elif request.method == "POST":
        flash(f"Update form validation failed: {update_form.errors}", "danger")

    return render_template("pq_detail.html", pq=pq, update_form=update_form)


@pq_bp.route("/<int:pq_id>/edit", methods=["GET", "POST"])
@login_required
def edit_pq(pq_id):
    pq = PQRecord.query.get_or_404(pq_id)

    # On POST, use submitted data.
    # On GET, populate from existing object.
    form = PQForm(request.form if request.method == "POST" else None, obj=pq)
    form.assigned_to_user_id.choices = get_active_user_choices()

    if request.method == "GET":
        form.assigned_to_user_id.data = pq.assigned_to_user_id or 0

    if form.validate_on_submit():
        try:
            old_status = pq.status
            old_assignee = pq.assigned_to_user_id

            pq.pq_reference_no = form.pq_reference_no.data.strip()
            pq.title = form.title.data.strip()
            pq.description = form.description.data.strip()
            pq.ministry_or_agency = form.ministry_or_agency.data.strip()
            pq.submitted_by = form.submitted_by.data.strip()
            pq.assigned_to_user_id = (
                None if form.assigned_to_user_id.data == 0 else form.assigned_to_user_id.data
            )
            pq.priority = form.priority.data
            pq.status = form.status.data
            pq.due_date = form.due_date.data
            pq.date_received = form.date_received.data

            if pq.status == "Closed" and not pq.date_closed:
                pq.date_closed = date.today()
            elif pq.status != "Closed":
                pq.date_closed = None

            if old_status != pq.status:
                db.session.add(
                    PQUpdate(
                        pq_id=pq.id,
                        update_text=f"Status changed from '{old_status}' to '{pq.status}'.",
                        update_type="Status Change",
                        updated_by_user_id=current_user.id,
                    )
                )

            if old_assignee != pq.assigned_to_user_id:
                db.session.add(
                    PQUpdate(
                        pq_id=pq.id,
                        update_text="Assignment updated.",
                        update_type="Assignment",
                        updated_by_user_id=current_user.id,
                    )
                )

            db.session.commit()

            flash("PQ updated successfully.", "success")
            return redirect(url_for("pq.view_pq", pq_id=pq.id))

        except IntegrityError:
            db.session.rollback()
            flash("PQ reference number already exists.", "danger")

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating PQ: {str(e)}", "danger")

    elif request.method == "POST":
        flash(f"Form validation failed: {form.errors}", "danger")

    return render_template("pq_create.html", form=form, is_edit=True, pq=pq)
