
from app import app
from extensions import db
from models.user import User
from getpass import getpass

with app.app_context():

    print("\n===== SmartHire Admin Account Creation =====")

    full_name = input("Enter Admin Name: ").strip()
    email = input("Enter Admin Email: ").strip().lower()
    password = input("Enter Admin Password: ")
    confirm_password = input("Confirm Admin Password: ")

    if not full_name or not email or not password:
        print("Error: All fields are required.")

    elif password != confirm_password:
        print("Error: Passwords do not match.")

    elif len(password) < 8:
        print("Error: Password must contain at least 8 characters.")

    elif User.query.filter_by(email=email).first():
        print("Error: This email already exists.")

    else:
        admin = User(
            full_name=full_name,
            email=email,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("\nAdmin account created successfully!")
