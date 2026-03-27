from app.extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # include these only if you actually have them
    full_name = db.Column(db.String(255), nullable=True)
    is_active_user = db.Column(db.Boolean, default=True, nullable=False)

    assigned_pqs = db.relationship(
        "PQRecord",
        foreign_keys="PQRecord.assigned_to_user_id",
        back_populates="assigned_user",
        lazy=True
    )

    pq_updates_made = db.relationship(
        "PQUpdate",
        foreign_keys="PQUpdate.updated_by_user_id",
        back_populates="updated_by",
        lazy=True
    )
