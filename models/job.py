
from extensions import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(100))

    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    skills_required = db.Column(db.String(500))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    recruiter = db.relationship(
        "User",
        backref=db.backref("posted_jobs", lazy=True)
    )
