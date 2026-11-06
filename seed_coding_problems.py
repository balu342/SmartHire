from app import app
from extensions import db
from models.coding_problem import CodingProblem
from seed_data.coding_questions import CODING_QUESTIONS


def seed_coding_problems():

    added_count = 0
    skipped_count = 0

    with app.app_context():

        for question in CODING_QUESTIONS:

            existing = CodingProblem.query.filter_by(
                title=question["title"]
            ).first()

            if existing:
                skipped_count += 1
                continue

            problem = CodingProblem(
                title=question["title"],
                description=question["description"],
                difficulty=question["difficulty"],
                category=question["category"],
                input_format=question["input_format"],
                output_format=question["output_format"],
                sample_input=question["sample_input"],
                sample_output=question["sample_output"],
                constraints=question["constraints"]
            )

            db.session.add(problem)
            added_count += 1

        db.session.commit()

        print("\nCoding Problems Database Updated!")
        print(f"New questions added: {added_count}")
        print(f"Already existing questions skipped: {skipped_count}")
        print(f"Total questions in database: {CodingProblem.query.count()}")


if __name__ == "__main__":
    seed_coding_problems()