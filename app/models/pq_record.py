from datetime import datetime
from app import db

class PQRecord(db.Model):
    __tablename__ = "pq_records"

    id = db.Column(db.Integer, primary_key=True)
    pq_reference_no = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    agency = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="New")
    priority = db.Column(db.String(50), default="Normal")
    assigned_to = db.Column(db.Integer, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    date_received = db.Column(db.Date, nullable=True)
    date_closed = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
