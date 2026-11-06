
from extensions import db
from datetime import datetime


class CodingProblem(db.Model):
    __tablename__ = "coding_problems"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    category = db.Column(db.String(100))

    input_format = db.Column(db.Text)

    output_format = db.Column(db.Text)

    sample_input = db.Column(db.Text)

    sample_output = db.Column(db.Text)

    constraints = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
