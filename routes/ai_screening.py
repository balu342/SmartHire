
import os
import re
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def extract_resume_text(file_path):
    """Extract text from an uploaded PDF resume."""

    try:
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

        return text.strip()

    except Exception as error:
        print("Resume extraction error:", error)
        return ""


def extract_skills(text):
    """Identify technical skills from resume text."""

    skills_list = [
        "Python", "Java", "C", "C++", "SQL", "MySQL",
        "HTML", "CSS", "JavaScript", "Flask", "Django",
        "React", "Node.js", "Machine Learning",
        "Deep Learning", "Artificial Intelligence",
        "Data Science", "Pandas", "NumPy",
        "TensorFlow", "Keras", "Scikit-learn",
        "Power BI", "Tableau", "Excel",
        "AWS", "Azure", "Docker", "Git",
        "REST API", "MongoDB", "PostgreSQL",
        "Hadoop", "Spark"
    ]

    normalized_text = text.lower()

    found_skills = []

    for skill in skills_list:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return found_skills


def calculate_match_score(resume_skills, required_skills):
    """Calculate the percentage of required skills matched."""

    if not required_skills:
        return 0

    required = {
        skill.strip().lower()
        for skill in required_skills.split(",")
        if skill.strip()
    }

    if not required:
        return 0

    matched = {
        skill.lower()
        for skill in resume_skills
    }

    matching_skills = required.intersection(matched)

    score = (len(matching_skills) / len(required)) * 100

    return round(score, 2)


def screen_resume(file_path, required_skills):
    """Extract skills and calculate resume matching score."""

    resume_text = extract_resume_text(file_path)

    if not resume_text:
        return {
            "skills": [],
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "error": "Unable to extract text from this PDF."
        }

    resume_skills = extract_skills(resume_text)

    required = [
        skill.strip()
        for skill in required_skills.split(",")
        if skill.strip()
    ]

    matched = [
        skill for skill in required
        if skill.lower() in [s.lower() for s in resume_skills]
    ]

    missing = [
        skill for skill in required
        if skill.lower() not in [s.lower() for s in resume_skills]
    ]

    return {
        "skills": resume_skills,
        "match_score": calculate_match_score(
            resume_skills,
            required_skills
        ),
        "matched_skills": matched,
        "missing_skills": missing,
        "error": None
    }
