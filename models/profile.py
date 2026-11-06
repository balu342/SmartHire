from extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(db.String(15))
    location = db.Column(db.String(150))
    headline = db.Column(db.String(200))
    career_summary = db.Column(db.Text)
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)

    user = db.relationship(
        "User",
        backref=db.backref("profile", uselist=False)
    )