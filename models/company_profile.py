
from extensions import db
from datetime import datetime


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)

    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    company_size = db.Column(db.String(50))
    location = db.Column(db.String(150))
    description = db.Column(db.Text)
    logo = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    recruiter = db.relationship(
        "User",
        backref=db.backref("company_profile", uselist=False)
    )
