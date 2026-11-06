from extensions import db
from datetime import datetime


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    saved_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship("User")
    job = db.relationship("Job")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "job_id",
            name="unique_saved_job"
        ),
    )