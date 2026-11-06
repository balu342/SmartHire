from app import app
from extensions import db
from sqlalchemy import inspect, text

with app.app_context():

    inspector = inspect(db.engine)

    columns = [
        column["name"]
        for column in inspector.get_columns("users")
    ]

    if "is_active" not in columns:

        db.session.execute(
            text("""
                ALTER TABLE users
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE
            """)
        )

        db.session.commit()

        print("SUCCESS! is_active column added to users table.")

    else:
        print("is_active column already exists.")

print("User table update completed!")
