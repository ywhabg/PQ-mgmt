from app.extensions import db


class SampleRecord(db.Model):
    __tablename__ = "sample_records"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
