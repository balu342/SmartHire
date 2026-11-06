
from extensions import db
from datetime import datetime


class Submission(db.Model):

    __tablename__ = "coding_submissions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    problem_id = db.Column(
        db.Integer,
        db.ForeignKey("coding_problems.id"),
        nullable=False
    )

    language = db.Column(db.String(30), nullable=False)

    source_code = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pending"
    )

    actual_output = db.Column(db.Text)

    execution_time = db.Column(db.String(50))

    memory = db.Column(db.Integer)

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("coding_submissions", lazy=True)
    )

    problem = db.relationship(
        "CodingProblem",
        backref=db.backref("coding_submissions", lazy=True)
    )

