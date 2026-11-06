
from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    applicant_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    cover_letter = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    job = db.relationship("Job")
    applicant = db.relationship("User")
