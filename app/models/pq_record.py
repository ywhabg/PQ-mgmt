from datetime import datetime
from app.extensions import db


class PQRecord(db.Model):
    __tablename__ = "pq_records"

    id = db.Column(db.Integer, primary_key=True)
    pq_reference_no = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ministry_or_agency = db.Column(db.String(150), nullable=False)
    submitted_by = db.Column(db.String(150), nullable=False)

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(50), nullable=False, default="New")

    due_date = db.Column(db.Date, nullable=True)
    date_received = db.Column(db.Date, nullable=True)
    date_closed = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    updates = db.relationship(
        "PQUpdate",
        backref="pq_record",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="desc(PQUpdate.created_at)"
    )


class PQUpdate(db.Model):
    __tablename__ = "pq_updates"

    id = db.Column(db.Integer, primary_key=True)
    pq_id = db.Column(db.Integer, db.ForeignKey("pq_records.id"), nullable=False)
    update_text = db.Column(db.Text, nullable=False)
    update_type = db.Column(db.String(50), nullable=False, default="General")
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
