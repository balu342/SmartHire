import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import Config
from extensions import db, login_manager
from models.user import User
from models.profile import Profile
from models.resume import Resume
from models.job import Job
from models.application import Application
from models.saved_job import SavedJob
from routes.ai_screening import screen_resume
from models.notification import Notification
from models.profile import Profile
from models.company_profile import CompanyProfile
from models.coding_problem import CodingProblem
from models.submission import Submission
import requests
import time

app = Flask(__name__)
app.config.from_object(Config)
app = Flask(__name__)

app.config.from_object(Config)

# Resume Upload Configuration
UPLOAD_FOLDER = os.path.join(
    app.root_path, "static", "uploads", "resumes"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# Initialize database and login manager
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"

# Load logged-in user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Unread Notification Count
@app.context_processor
def inject_unread_notification_count():

    if current_user.is_authenticated:
        unread_notification_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
    else:
        unread_notification_count = 0

    return {
        "unread_notification_count": unread_notification_count
    }


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "job_seeker")

        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        new_user = User(
            full_name=full_name,
            email=email,
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)
            flash("Login successful!", "success")

            # Admin Login
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            # Job Seeker Login
            elif user.role == "job_seeker":
                return redirect(url_for("job_seeker_dashboard"))

            # Recruiter Login
            elif user.role == "recruiter":
                return redirect(url_for("recruiter_dashboard"))

            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            else:
                logout_user()
                flash("Invalid user role.", "danger")
                return redirect(url_for("login"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

# Dashboard page

# General Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))

    elif current_user.role == "job_seeker":
        return redirect(url_for("job_seeker_dashboard"))

    elif current_user.role == "recruiter":
        return redirect(url_for("recruiter_dashboard"))

    flash("Invalid user role.", "danger")
    return redirect(url_for("login"))

# Job Seeker Dashboard
@app.route("/job-seeker/dashboard")
@login_required
def job_seeker_dashboard():

    if current_user.role != "job_seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    saved_jobs_count = SavedJob.query.filter_by(
        user_id=current_user.id
    ).count()

    applications_count = Application.query.filter_by(
        applicant_id=current_user.id
    ).count()

    return render_template(
        "job_seeker_dashboard.html",
        saved_jobs_count=saved_jobs_count,
        applications_count=applications_count
    )
# SmartHire Coding Problem Library
@app.route("/coding-problems")
@login_required
def coding_problems():

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    search_query = request.args.get("search", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()
    category_filter = request.args.get("category", "").strip()

    query = CodingProblem.query

    # Search questions
    if search_query:
        query = query.filter(
            CodingProblem.title.ilike(f"%{search_query}%") |
            CodingProblem.description.ilike(f"%{search_query}%")
        )

    # Difficulty filter
    if difficulty_filter in ["Easy", "Medium", "Hard"]:
        query = query.filter_by(difficulty=difficulty_filter)

    # Category filter
    if category_filter:
        query = query.filter_by(category=category_filter)

    problems = query.order_by(CodingProblem.id.asc()).all()

    categories = [
        item[0] for item in
        db.session.query(CodingProblem.category)
        .filter(CodingProblem.category.isnot(None))
        .distinct()
        .order_by(CodingProblem.category)
        .all()
    ]

    return render_template(
        "coding_problems.html",
        problems=problems,
        categories=categories,
        search_query=search_query,
        difficulty_filter=difficulty_filter,
        category_filter=category_filter
    )
# Recruiter Dashboard
@app.route("/recruiter/dashboard")
@login_required
def recruiter_dashboard():

    if current_user.role != "recruiter":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    company = CompanyProfile.query.filter_by(
        recruiter_id=current_user.id
    ).first()

    return render_template(
        "recruiter_dashboard.html",
        company=company
    )
    

    if current_user.role != "recruiter":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("recruiter_dashboard.html")
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if current_user.role != "job_seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    user_profile = Profile.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":

        if not user_profile:
            user_profile = Profile(user_id=current_user.id)
            db.session.add(user_profile)

        current_user.full_name = request.form.get("full_name")

        user_profile.phone = request.form.get("phone")
        user_profile.location = request.form.get("location")
        user_profile.headline = request.form.get("headline")
        user_profile.career_summary = request.form.get("career_summary")
        user_profile.skills = request.form.get("skills")
        user_profile.education = request.form.get("education")
        user_profile.experience = request.form.get("experience")

        db.session.commit()

        flash("Profile saved successfully!", "success")

        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        profile=user_profile
    )


@app.route("/post-job", methods=["GET", "POST"])
@login_required
def post_job():

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":

        job = Job(
            recruiter_id=current_user.id,
            job_title=request.form.get("job_title"),
            company_name=request.form.get("company_name"),
            location=request.form.get("location"),
            job_type=request.form.get("job_type"),
            salary=request.form.get("salary"),
            description=request.form.get("description"),
            requirements=request.form.get("requirements"),
            skills_required=request.form.get("skills_required")
        )

        db.session.add(job)
        db.session.commit()

        flash("Job published successfully!", "success")
        return redirect(url_for("job_success"))
    
    return render_template("post_job.html")


@app.route("/job-success")
@login_required
def job_success():

    if current_user.role != "recruiter":
        return redirect(url_for("home"))

    return render_template("job_success.html")

@app.route("/manage-jobs")
@login_required
def manage_jobs():
    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    jobs = Job.query.filter_by(
        recruiter_id=current_user.id
    ).order_by(Job.created_at.desc()).all()

    return render_template("manage_jobs.html", jobs=jobs)


# MODULE 17: RECRUITMENT ANALYTICS

@app.route("/recruitment-analytics")
@login_required
def recruitment_analytics():
    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    jobs = Job.query.filter_by(
        recruiter_id=current_user.id
    ).all()

    total_jobs = len(jobs)

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).all()

    total_applications = len(applications)

    pending_count = sum(
        1 for app in applications if app.status == "Pending"
    )

    shortlisted_count = sum(
        1 for app in applications if app.status == "Shortlisted"
    )

    selected_count = sum(
        1 for app in applications if app.status == "Selected"
    )

    rejected_count = sum(
        1 for app in applications if app.status == "Rejected"
    )

    job_labels = [job.job_title for job in jobs]

    application_counts = [
        sum(1 for app in applications if app.job_id == job.id)
        for job in jobs
    ]

    return render_template(
        "recruitment_analytics.html",
        total_jobs=total_jobs,
        total_applications=total_applications,
        pending_count=pending_count,
        shortlisted_count=shortlisted_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        job_labels=job_labels,
        application_counts=application_counts
    )




    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    jobs = Job.query.filter_by(
        recruiter_id=current_user.id
    ).order_by(Job.created_at.desc()).all()

    return render_template("manage_jobs.html", jobs=jobs)
# Recruiter - View Applicants
# Recruiter - View Applicants
@app.route("/view-applicants")
@login_required
def view_applicants():

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(Application.applied_at.desc()).all()

    return render_template(
        "view_applicants.html",
        applications=applications
    )


# MODULE 20: COMPANY PROFILE MANAGEMENT


@app.route("/company-profile", methods=["GET", "POST"])
@login_required
def company_profile():

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    company = CompanyProfile.query.filter_by(
        recruiter_id=current_user.id
    ).first()

    if request.method == "POST":

        company_name = request.form.get("company_name", "").strip()

        if not company_name:
            flash("Company name is required.", "danger")
            return redirect(url_for("recruiter_dashboard"))

        # Get uploaded logo
        logo_file = request.files.get("logo")

        # Validate logo extension
        if logo_file and logo_file.filename:
            extension = os.path.splitext(logo_file.filename)[1].lower()

            allowed_extensions = [".png", ".jpg", ".jpeg", ".webp"]

            if extension not in allowed_extensions:
                flash("Upload PNG, JPG, JPEG or WEBP logo only.", "danger")
                return redirect(url_for("recruiter_dashboard"))

        # Create company profile if it does not exist
        if company is None:
            company = CompanyProfile(
                recruiter_id=current_user.id,
                company_name=company_name
            )
            db.session.add(company)

        company.company_name = company_name
        company.industry = request.form.get("industry", "").strip()
        company.website = request.form.get("website", "").strip()
        company.company_size = request.form.get("company_size", "").strip()
        company.location = request.form.get("location", "").strip()
        company.description = request.form.get("description", "").strip()

        # Save company logo
        if logo_file and logo_file.filename:
            logo_folder = os.path.join(
                app.static_folder,
                "company_logos"
            )

            os.makedirs(logo_folder, exist_ok=True)

            filename = secure_filename(
                f"company_{current_user.id}_{os.urandom(8).hex()}{extension}"
            )

            logo_path = os.path.join(logo_folder, filename)
            logo_file.save(logo_path)

            company.logo = f"company_logos/{filename}"

        try:
            db.session.commit()
            flash("Company profile saved successfully!", "success")

        except Exception:
            db.session.rollback()
            flash("Unable to save company profile. Please try again.", "danger")

        return redirect(url_for("recruiter_dashboard"))

    return render_template(
        "company_profile.html",
        company=company
    )


    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    company = CompanyProfile.query.filter_by(
        recruiter_id=current_user.id
    ).first()

    if request.method == "POST":

        company_name = request.form.get("company_name", "").strip()

        if not company_name:
            flash("Company name is required.", "danger")
            return redirect(url_for("recruiter_dashboard"))

        if company is None:
            company = CompanyProfile(
                recruiter_id=current_user.id,
                company_name=company_name
            )
            db.session.add(company)

        company.company_name = company_name
        company.industry = request.form.get("industry", "").strip()
        company.website = request.form.get("website", "").strip()
        company.company_size = request.form.get("company_size", "").strip()
        company.location = request.form.get("location", "").strip()
        company.description = request.form.get("description", "").strip()

        try:
            db.session.commit()
            flash("Company profile saved successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Unable to save company profile. Please try again.", "danger")

        return redirect(url_for("company_profile"))

    return render_template(
        "company_profile.html",
        company=company
    )


@app.route("/candidate-search")
@login_required
def candidate_search():

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    search = request.args.get("search", "").strip()
    skill = request.args.get("skill", "").strip()
    location = request.args.get("location", "").strip()

    query = User.query.join(
        Profile,
        User.id == Profile.user_id
    ).filter(
        User.role == "job_seeker"
    )

    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if skill:
        query = query.filter(
            Profile.skills.ilike(f"%{skill}%")
        )

    if location:
        query = query.filter(
            Profile.location.ilike(f"%{location}%")
        )

    candidates = query.order_by(
        User.full_name.asc()
    ).all()

    return render_template(
        "candidate_search.html",
        candidates=candidates,
        search=search,
        skill=skill,
        location=location
    )


    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    return render_template(
        "view_applicants.html",
        applications=applications
    )

# Recruiter - Update Application Status
@app.route("/update-application-status/<int:application_id>", methods=["POST"])
@login_required
def update_application_status(application_id):

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    application = Application.query.get_or_404(application_id)

    if application.job.recruiter_id != current_user.id:
        flash("You cannot update this application.", "danger")
        return redirect(url_for("view_applicants"))

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Shortlisted",
        "Rejected",
        "Selected"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid application status.", "danger")
        return redirect(url_for("view_applicants"))

    try:
        old_status = application.status

        if old_status != new_status:
            application.status = new_status

            # Notify the job seeker about the status change
            notification = Notification(
                user_id=application.applicant_id,
                message=f"Your application for {application.job.job_title} is now {new_status}.",
                notification_type="application_status"
            )

            db.session.add(notification)
            db.session.commit()

            flash(
                f"Application status updated to {new_status} successfully!",
                "success"
            )
        else:
            flash("The application already has this status.", "info")

    except Exception:
        db.session.rollback()
        flash("Unable to update application status.", "danger")

    return redirect(url_for("view_applicants"))
    try:
        application.status = new_status
        db.session.commit()

        flash(
            f"Application status updated to {new_status} successfully!",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash("Unable to update application status.", "danger")

    return redirect(url_for("view_applicants"))

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    return render_template(
        "view_applicants.html",
        applications=applications
    )

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Shortlisted",
        "Rejected",
        "Selected"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid application status.", "danger")
        return redirect(url_for("view_applicants"))

    try:
        application.status = new_status
        db.session.commit()

        flash(
            f"Application status updated to {new_status} successfully!",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash("Unable to update application status.", "danger")

    return redirect(url_for("view_applicants"))

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    return render_template(
        "view_applicants.html",
        applications=applications
    )

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Shortlisted",
        "Rejected",
        "Selected"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid application status.", "danger")
        return redirect(url_for("view_applicants"))

    try:
        application.status = new_status
        db.session.commit()

        flash(
            f"Application status updated to {new_status} successfully!",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash("Unable to update application status.", "danger")

    return redirect(url_for("view_applicants"))
    
    
    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    return render_template(
        "view_applicants.html",
        applications=applications
    )
@app.route("/job-search", methods=["GET", "POST"])
@login_required

def job_search():
    

    if current_user.role != "job_seeker":
        flash("Only job seekers can search for jobs.", "danger")
        return redirect(url_for("home"))

    search_query = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()

    jobs_query = Job.query

    if search_query:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.job_title.ilike(f"%{search_query}%"),
                Job.company_name.ilike(f"%{search_query}%"),
                Job.skills_required.ilike(f"%{search_query}%")
            )
        )

    if location:
        jobs_query = jobs_query.filter(
            Job.location.ilike(f"%{location}%")
        )

    if job_type:
        jobs_query = jobs_query.filter_by(job_type=job_type)

    jobs = jobs_query.order_by(Job.created_at.desc()).all()

    return render_template(
        "job_search.html",
        jobs=jobs,
        search_query=search_query,
        location=location,
        selected_job_type=job_type
    )
# Save a Job
@app.route("/save-job/<int:job_id>", methods=["POST"])
@login_required
def save_job(job_id):

    if current_user.role != "job_seeker":
        flash("Only job seekers can save jobs.", "danger")
        return redirect(url_for("home"))

    job = Job.query.get_or_404(job_id)

    existing_saved_job = SavedJob.query.filter_by(
        user_id=current_user.id,
        job_id=job.id
    ).first()

    if existing_saved_job:
        flash("You have already saved this job.", "warning")
    else:
        saved_job = SavedJob(
            user_id=current_user.id,
            job_id=job.id
        )

        db.session.add(saved_job)
        db.session.commit()

        flash("Job saved successfully!", "success")

    return redirect(request.referrer or url_for("job_search"))


# View Saved Jobs
@app.route("/saved-jobs")
@login_required
def saved_jobs():

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    saved_jobs_list = SavedJob.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SavedJob.saved_at.desc()
    ).all()

    return render_template(
        "saved_jobs.html",
        saved_jobs=saved_jobs_list
    )


# Remove a Saved Job
@app.route("/remove-saved-job/<int:saved_job_id>", methods=["POST"])
@login_required
def remove_saved_job(saved_job_id):

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    saved_job = SavedJob.query.filter_by(
        id=saved_job_id,
        user_id=current_user.id
    ).first_or_404()

    try:
        db.session.delete(saved_job)
        db.session.commit()
        flash("Saved job removed successfully!", "success")

    except Exception:
        db.session.rollback()
        flash("Unable to remove saved job.", "danger")

    return redirect(url_for("saved_jobs"))

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    saved_jobs_list = SavedJob.query.filter_by(
        user_id=current_user.id
    ).order_by(
        SavedJob.saved_at.desc()
    ).all()

    return render_template(
        "saved_jobs.html",
        saved_jobs=saved_jobs_list
    )
@app.route("/my-applications")
@login_required
def my_applications():

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.filter_by(
        applicant_id=current_user.id
    ).order_by(Application.applied_at.desc()).all()

    return render_template(
        "applications.html",
        applications=applications
    )

# Job Details
@app.route("/job-details/<int:job_id>")
@login_required
def job_details(job_id):

    if current_user.role != "job_seeker":
        flash("Only job seekers can view job details.", "danger")
        return redirect(url_for("home"))

    job = Job.query.get_or_404(job_id)

    # Get company profile and logo
    company_profile = CompanyProfile.query.filter_by(
        recruiter_id=job.recruiter_id
    ).first()

    return render_template(
        "job_details.html",
        job=job,
        company_profile=company_profile
    )

@app.route("/resume", methods=["GET", "POST"])
@login_required
def resume():

    if current_user.role != "job_seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        if "resume" not in request.files:
            flash("Please select a PDF resume.", "danger")
            return redirect(url_for("resume"))

        file = request.files["resume"]

        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("resume"))

        if not allowed_file(file.filename):
            flash("Only PDF files are allowed.", "danger")
            return redirect(url_for("resume"))

        if file.mimetype != "application/pdf":
            flash("Please upload a valid PDF file.", "danger")
            return redirect(url_for("resume"))

        filename = secure_filename(file.filename)

        # Add a unique prefix to avoid filename conflicts
        unique_filename = f"user_{current_user.id}_{filename}"

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        file.save(file_path)

        new_resume = Resume(
            user_id=current_user.id,
            file_name=filename,
            file_path=unique_filename
        )

        db.session.add(new_resume)
        db.session.commit()

        flash("Resume uploaded successfully!", "success")
        return redirect(url_for("resume"))

    resumes = Resume.query.filter_by(
        user_id=current_user.id
    ).order_by(Resume.uploaded_at.desc()).all()

    return render_template(
        "resume.html",
        resumes=resumes
    )
@app.route("/view-resume/<int:resume_id>")
@login_required
def view_resume(resume_id):

    if current_user.role != "job_seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=current_user.id
    ).first_or_404()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        resume.file_path,
        mimetype="application/pdf",
        as_attachment=False
    )
# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# Apply for Job
@app.route("/apply-job/<int:job_id>", methods=["GET", "POST"])
@login_required
def apply_job(job_id):

    if current_user.role != "job_seeker":
        flash("Only job seekers can apply for jobs.", "danger")
        return redirect(url_for("home"))

    job = Job.query.get_or_404(job_id)

    existing_application = Application.query.filter_by(
        job_id=job.id,
        applicant_id=current_user.id
    ).first()

    if existing_application:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("job_details", job_id=job.id))

    if request.method == "POST":
        cover_letter = request.form.get("cover_letter", "").strip()

        application = Application(
            job_id=job.id,
            applicant_id=current_user.id,
            cover_letter=cover_letter
        )

        db.session.add(application)

        # Create notification for recruiter
        notification = Notification(
            user_id=job.recruiter_id,
            message=f"{current_user.full_name} applied for the job: {job.job_title}",
            notification_type="new_application"
        )

        db.session.add(notification)

        db.session.commit()

        flash("Your application was submitted successfully!", "success")
        return redirect(url_for("job_details", job_id=job.id))

    return render_template("apply_job.html", job=job)

@app.route("/ai-resume-screening/<int:job_id>")
@login_required
def ai_resume_screening(job_id):

    if current_user.role != "recruiter":
        flash("Access denied. Recruiters only.", "danger")
        return redirect(url_for("home"))

    job = Job.query.filter_by(
        id=job_id,
        recruiter_id=current_user.id
    ).first_or_404()

    applications = Application.query.filter_by(
        job_id=job.id
    ).order_by(Application.applied_at.desc()).all()

    screening_results = []

    for application in applications:

        resume = Resume.query.filter_by(
            user_id=application.applicant_id
        ).order_by(Resume.uploaded_at.desc()).first()

        if not resume:
            continue

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume.file_path
        )

        if not os.path.isfile(file_path):
            continue

        result = screen_resume(
            file_path,
            job.skills_required or ""
        )

        screening_results.append({
            "applicant": application.applicant,
            "resume": resume,
            "result": result,
            "application": application
        })

    screening_results.sort(
        key=lambda item: item["result"]["match_score"],
        reverse=True
    )

    return render_template(
        "ai_resume_screening.html",
        job=job,
        screening_results=screening_results
    )
# Display Notifications
@app.route("/notifications")
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        "notifications.html",
        notifications=user_notifications
    )


# Mark Notification as Read
@app.route("/mark-notification-read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()

    notification.is_read = True
    db.session.commit()

    flash("Notification marked as read.", "success")
    return redirect(url_for("notifications"))


# Delete Notification
@app.route("/delete-notification/<int:notification_id>", methods=["POST"])
@login_required
def delete_notification(notification_id):

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(notification)
    db.session.commit()

    flash("Notification deleted successfully.", "success")
    return redirect(url_for("notifications"))
# SmartHire Coding Practice Dashboard
@app.route("/coding-practice")
@login_required
def coding_practice():

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    total_problems = CodingProblem.query.count()

    easy_count = CodingProblem.query.filter_by(
        difficulty="Easy"
    ).count()

    medium_count = CodingProblem.query.filter_by(
        difficulty="Medium"
    ).count()

    hard_count = CodingProblem.query.filter_by(
        difficulty="Hard"
    ).count()

    return render_template(
        "coding_practice.html",
        total_problems=total_problems,
        easy_count=easy_count,
        medium_count=medium_count,
        hard_count=hard_count
    )
# SmartHire Individual Coding Problem
@app.route("/coding-problem/<int:problem_id>")
@login_required
def coding_problem_detail(problem_id):

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    problem = CodingProblem.query.get_or_404(problem_id)

    return render_template(
        "coding_problem_detail.html",
        problem=problem
    )
# SmartHire - Judge0 Code Execution API
@app.route("/run-code", methods=["POST"])
@login_required
def run_code():

    if current_user.role != "job_seeker":
        return jsonify({
            "success": False,
            "message": "Access denied."
        }), 403

    data = request.get_json(silent=True) or {}

    source_code = data.get("code", "")
    language = data.get("language", "python")
    custom_input = data.get("input", "")

    if not source_code.strip():
        return jsonify({
            "success": False,
            "message": "Please write your code first."
        }), 400

    if len(source_code) > 50000:
        return jsonify({
            "success": False,
            "message": "Code is too large."
        }), 400

    language_ids = {
        "python": 71,
        "java": 62,
        "cpp": 54
    }

    if language not in language_ids:
        return jsonify({
            "success": False,
            "message": "Unsupported programming language."
        }), 400

    api_url = os.getenv(
        "JUDGE0_API_URL",
        "https://ce.judge0.com"
    )

    try:
        # Send code to Judge0
        submission = requests.post(
            f"{api_url}/submissions",
            params={
                "base64_encoded": "false",
                "wait": "false"
            },
            json={
                "source_code": source_code,
                "language_id": language_ids[language],
                "stdin": custom_input
            },
            timeout=15
        )

        submission.raise_for_status()
        token = submission.json().get("token")

        if not token:
            return jsonify({
                "success": False,
                "message": "Judge0 did not return a submission token."
            }), 502

        # Wait for execution result
        result = None

        for attempt in range(15):
            time.sleep(1)

            response = requests.get(
                f"{api_url}/submissions/{token}",
                params={"base64_encoded": "false"},
                timeout=15
            )

            response.raise_for_status()
            result = response.json()

            status_id = result.get("status", {}).get("id")

            # 1 and 2 mean queued or processing
            if status_id not in [1, 2]:
                break

        if result is None or result.get("status", {}).get("id") in [1, 2]:
            return jsonify({
                "success": False,
                "message": "Execution is taking too long. Please try again."
            }), 504

        return jsonify({
            "success": True,
            "status": result.get("status", {}).get("description"),
            "output": result.get("stdout") or "",
            "error": result.get("stderr") or "",
            "compile_output": result.get("compile_output") or "",
            "execution_time": result.get("time"),
            "memory": result.get("memory")
        })

    except requests.exceptions.RequestException:
        return jsonify({
            "success": False,
            "message": "Unable to connect to Judge0. Please try again."
        }), 502
    
# SmartHire - Submit and Evaluate Coding Solution
@app.route("/submit-code", methods=["POST"])
@login_required
def submit_code():

    if current_user.role != "job_seeker":
        return jsonify({
            "success": False,
            "message": "Access denied."
        }), 403

    data = request.get_json(silent=True) or {}

    source_code = data.get("code", "").strip()
    language = data.get("language", "python")
    problem_id = data.get("problem_id")

    if not source_code:
        return jsonify({
            "success": False,
            "message": "Please write your solution first."
        }), 400

    if len(source_code) > 50000:
        return jsonify({
            "success": False,
            "message": "Code is too large."
        }), 400

    language_ids = {
        "python": 71,
        "java": 62,
        "cpp": 54
    }

    if language not in language_ids:
        return jsonify({
            "success": False,
            "message": "Unsupported language."
        }), 400

    problem = db.session.get(CodingProblem, problem_id)

    if not problem:
        return jsonify({
            "success": False,
            "message": "Coding problem not found."
        }), 404

    api_url = os.getenv(
        "JUDGE0_API_URL",
        "https://ce.judge0.com"
    )

    try:

        # Use the problem's sample input for evaluation
        judge_submission = requests.post(
            f"{api_url}/submissions",
            params={
                "base64_encoded": "false",
                "wait": "false"
            },
            json={
                "source_code": source_code,
                "language_id": language_ids[language],
                "stdin": problem.sample_input or ""
            },
            timeout=15
        )

        judge_submission.raise_for_status()

        token = judge_submission.json().get("token")

        if not token:
            return jsonify({
                "success": False,
                "message": "Judge0 did not return a token."
            }), 502

        result = None

        # Poll Judge0 for execution result
        for attempt in range(20):

            time.sleep(1)

            response = requests.get(
                f"{api_url}/submissions/{token}",
                params={
                    "base64_encoded": "false"
                },
                timeout=15
            )

            response.raise_for_status()
            result = response.json()

            status_id = result.get("status", {}).get("id")

            if status_id not in [1, 2]:
                break

        if result is None or result.get("status", {}).get("id") in [1, 2]:
            return jsonify({
                "success": False,
                "message": "Execution timed out. Please try again."
            }), 504

        judge_status = result.get("status", {}).get("description", "Error")

        actual_output = (
            result.get("stdout")
            or result.get("stderr")
            or result.get("compile_output")
            or ""
        )

        expected_output = (problem.sample_output or "").strip()
        received_output = (result.get("stdout") or "").strip()

        # Compare actual output with expected sample output
        if judge_status == "Accepted":

            if received_output == expected_output:
                final_status = "Accepted"
            else:
                final_status = "Wrong Answer"

        else:
            final_status = judge_status

        # Save submission in MySQL
        new_submission = Submission(
            user_id=current_user.id,
            problem_id=problem.id,
            language=language,
            source_code=source_code,
            status=final_status,
            actual_output=actual_output,
            execution_time=str(result.get("time") or ""),
            memory=result.get("memory")
        )

        db.session.add(new_submission)
        db.session.commit()

        return jsonify({
            "success": True,
            "status": final_status,
            "output": result.get("stdout") or "",
            "error": result.get("stderr") or "",
            "compile_output": result.get("compile_output") or "",
            "expected_output": expected_output,
            "execution_time": result.get("time"),
            "memory": result.get("memory"),
            "submission_id": new_submission.id
        })

    except requests.exceptions.RequestException:

        return jsonify({
            "success": False,
            "message": "Unable to connect to Judge0."
        }), 502

    except Exception:

        db.session.rollback()

        app.logger.exception("Coding submission failed")

        return jsonify({
            "success": False,
            "message": "Unable to save or evaluate your submission."
        }), 500
    

# SmartHire - View Individual Coding Submission
@app.route("/coding-submission/<int:submission_id>")
@login_required
def view_coding_submission(submission_id):

    if current_user.role != "job_seeker":
        flash("Access denied.", "danger")
        return redirect(url_for("home"))

    submission = Submission.query.filter_by(
        id=submission_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "view_coding_submission.html",
        submission=submission
    )


    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    submissions = Submission.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Submission.submitted_at.desc()
    ).all()

    total_submissions = len(submissions)

    accepted_count = Submission.query.filter_by(
        user_id=current_user.id,
        status="Accepted"
    ).count()

    wrong_count = Submission.query.filter_by(
        user_id=current_user.id,
        status="Wrong Answer"
    ).count()

    solved_count = db.session.query(
        Submission.problem_id
    ).filter_by(
        user_id=current_user.id,
        status="Accepted"
    ).distinct().count()

    accuracy = (
        round((accepted_count / total_submissions) * 100, 2)
        if total_submissions > 0 else 0
    )

    return render_template(
        "coding_submissions.html",
        submissions=submissions,
        total_submissions=total_submissions,
        accepted_count=accepted_count,
        wrong_count=wrong_count,
        solved_count=solved_count,
        accuracy=accuracy
    )
# SmartHire - Coding Submission History
@app.route("/coding-submissions")
@login_required
def coding_submissions():
    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    submissions = Submission.query.filter_by(
        user_id=current_user.id
    ).order_by(Submission.submitted_at.desc()).all()

    total_submissions = len(submissions)

    accepted_count = Submission.query.filter_by(
        user_id=current_user.id,
        status="Accepted"
    ).count()

    wrong_count = Submission.query.filter_by(
        user_id=current_user.id,
        status="Wrong Answer"
    ).count()

    solved_count = db.session.query(
        Submission.problem_id
    ).filter_by(
        user_id=current_user.id,
        status="Accepted"
    ).distinct().count()

    accuracy = (
        round((accepted_count / total_submissions) * 100, 2)
        if total_submissions > 0 else 0
    )

    return render_template(
        "coding_submissions.html",
        submissions=submissions,
        total_submissions=total_submissions,
        accepted_count=accepted_count,
        wrong_count=wrong_count,
        solved_count=solved_count,
        accuracy=accuracy
    )

# SmartHire - Coding Achievements and Progress Tracking

@app.route("/coding-progress")
@login_required
def coding_progress():

    if current_user.role != "job_seeker":
        flash("Access denied. Job seekers only.", "danger")
        return redirect(url_for("home"))

    submissions = Submission.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Submission.submitted_at.desc()
    ).all()

    total_submissions = len(submissions)

    accepted_submissions = [
        submission for submission in submissions
        if submission.status == "Accepted"
    ]

    accepted_count = len(accepted_submissions)

    solved_problem_ids = {
        submission.problem_id
        for submission in accepted_submissions
    }

    solved_count = len(solved_problem_ids)

    easy_solved = 0
    medium_solved = 0
    hard_solved = 0

    for problem_id in solved_problem_ids:
        problem = CodingProblem.query.get(problem_id)

        if problem:
            if problem.difficulty == "Easy":
                easy_solved += 1
            elif problem.difficulty == "Medium":
                medium_solved += 1
            elif problem.difficulty == "Hard":
                hard_solved += 1

    accuracy = (
        round((accepted_count / total_submissions) * 100, 2)
        if total_submissions > 0 else 0
    )

    total_problems = CodingProblem.query.count()

    easy_count = CodingProblem.query.filter_by(
        difficulty="Easy"
    ).count()

    medium_count = CodingProblem.query.filter_by(
        difficulty="Medium"
    ).count()

    hard_count = CodingProblem.query.filter_by(
        difficulty="Hard"
    ).count()

    progress = (
        round((solved_count / total_problems) * 100, 2)
        if total_problems > 0 else 0
    )

    achievements = [
        {
            "title": "First Solve",
            "description": "Solved your first coding problem",
            "icon": "fa-flag-checkered",
            "unlocked": solved_count >= 1
        },
        {
            "title": "Problem Solver",
            "description": "Solved 5 coding problems",
            "icon": "fa-medal",
            "unlocked": solved_count >= 5
        },
        {
            "title": "Rising Coder",
            "description": "Solved 10 coding problems",
            "icon": "fa-trophy",
            "unlocked": solved_count >= 10
        },
        {
            "title": "Coding Champion",
            "description": "Solved 25 coding problems",
            "icon": "fa-crown",
            "unlocked": solved_count >= 25
        },
        {
            "title": "Coding Master",
            "description": "Solved 50 coding problems",
            "icon": "fa-star",
            "unlocked": solved_count >= 50
        }
    ]

    return render_template(
        "coding_progress.html",
        total_submissions=total_submissions,
        accepted_count=accepted_count,
        solved_count=solved_count,
        easy_solved=easy_solved,
        medium_solved=medium_solved,
        hard_solved=hard_solved,
        easy_count=easy_count,
        medium_count=medium_count,
        hard_count=hard_count,
        accuracy=accuracy,
        total_problems=total_problems,
        progress=progress,
        achievements=achievements,
        recent_submissions=submissions[:5]
    )


@app.route("/admin-dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    # Platform statistics
    total_users = User.query.count()
    total_job_seekers = User.query.filter_by(role="job_seeker").count()
    total_recruiters = User.query.filter_by(role="recruiter").count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    total_companies = CompanyProfile.query.count()

    # User management data
    users = User.query.order_by(User.id.desc()).all()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()

    # Application status analytics
    applications = Application.query.all()

    pending_count = sum(
        1 for app in applications if app.status == "Pending"
    )
    shortlisted_count = sum(
        1 for app in applications if app.status == "Shortlisted"
    )
    selected_count = sum(
        1 for app in applications if app.status == "Selected"
    )
    rejected_count = sum(
        1 for app in applications if app.status == "Rejected"
    )

    # Job-wise application analytics
    jobs = Job.query.order_by(Job.created_at.desc()).all()

    job_labels = [job.job_title for job in jobs]

    application_counts = [
        Application.query.filter_by(job_id=job.id).count()
        for job in jobs
    ]

    # Recent applications
    recent_applications = Application.query.order_by(
        Application.applied_at.desc()
    ).limit(5).all()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_job_seekers=total_job_seekers,
        total_recruiters=total_recruiters,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_companies=total_companies,
        users=users,
        active_users=active_users,
        inactive_users=inactive_users,
        pending_count=pending_count,
        shortlisted_count=shortlisted_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        job_labels=job_labels,
        application_counts=application_counts,
        recent_applications=recent_applications
    )

# MODULE 28: ADMIN JOB MANAGEMENT

@app.route("/admin/jobs")
@login_required
def admin_job_management():

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    jobs = Job.query.order_by(
        Job.created_at.desc()
    ).all()

    total_jobs = Job.query.count()

    return render_template(
        "admin_jobs.html",
        jobs=jobs,
        total_jobs=total_jobs
    )


@app.route("/admin/delete-job/<int:job_id>", methods=["POST"])
@login_required
def admin_delete_job(job_id):

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    job = Job.query.get_or_404(job_id)

    # Delete related applications first
    Application.query.filter_by(job_id=job.id).delete()

    # Delete related saved jobs
    SavedJob.query.filter_by(job_id=job.id).delete()

    db.session.delete(job)
    db.session.commit()

    flash("Job posting deleted successfully.", "success")

    return redirect(url_for("admin_job_management"))
# MODULE 29: ADMIN APPLICATION MANAGEMENT

@app.route("/admin/applications")
@login_required
def admin_application_management():

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    applications = Application.query.order_by(
        Application.applied_at.desc()
    ).all()

    total_applications = Application.query.count()

    return render_template(
        "admin_applications.html",
        applications=applications,
        total_applications=total_applications
    )


@app.route(
    "/admin/update-application/<int:application_id>",
    methods=["POST"]
)
@login_required
def admin_update_application(application_id):

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    application = Application.query.get_or_404(application_id)

    new_status = request.form.get("status")

    allowed_statuses = [
        "Pending",
        "Reviewed",
        "Shortlisted",
        "Rejected",
        "Accepted"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid application status.", "danger")
        return redirect(url_for("admin_application_management"))

    application.status = new_status
    db.session.commit()

    flash("Application status updated successfully.", "success")

    return redirect(url_for("admin_application_management"))


@app.route("/admin/users")
@login_required
def admin_users():

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    users = User.query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        "admin_users.html",
        users=users
    )
@app.route("/admin/user/<int:user_id>/toggle-status", methods=["POST"])
@login_required
def toggle_user_status(user_id):

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)

    if user.role == "admin":
        flash("Admin accounts cannot be deactivated here.", "warning")
        return redirect(url_for("admin_dashboard") + "#user-management")

    user.is_active = not user.is_active

    db.session.commit()

    status = "activated" if user.is_active else "deactivated"

    flash(
        f"User account successfully {status}.",
        "success"
    )

    return redirect(url_for("admin_dashboard") + "#user-management")

# MODULE 30: ADMIN REPORTS & PLATFORM ANALYTICS

@app.route("/admin/reports")
@login_required
def admin_reports():

    if current_user.role != "admin":
        flash("Access denied! Admin access only.", "danger")
        return redirect(url_for("home"))

    # Platform statistics
    total_users = User.query.count()
    total_job_seekers = User.query.filter_by(role="job_seeker").count()
    total_recruiters = User.query.filter_by(role="recruiter").count()

    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    # Application status statistics
    applications = Application.query.all()

    pending_count = sum(
        1 for application in applications
        if application.status == "Pending"
    )

    shortlisted_count = sum(
        1 for application in applications
        if application.status == "Shortlisted"
    )

    selected_count = sum(
        1 for application in applications
        if application.status == "Selected"
    )

    rejected_count = sum(
        1 for application in applications
        if application.status == "Rejected"
    )

    # Job-wise application statistics
    jobs = Job.query.order_by(Job.created_at.desc()).all()

    job_labels = [job.job_title for job in jobs]

    application_counts = [
        Application.query.filter_by(job_id=job.id).count()
        for job in jobs
    ]

    # Recent applications
    recent_applications = Application.query.order_by(
        Application.applied_at.desc()
    ).limit(5).all()

    return render_template(
        "admin_reports.html",
        total_users=total_users,
        total_job_seekers=total_job_seekers,
        total_recruiters=total_recruiters,
        total_jobs=total_jobs,
        total_applications=total_applications,
        pending_count=pending_count,
        shortlisted_count=shortlisted_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        job_labels=job_labels,
        application_counts=application_counts,
        recent_applications=recent_applications
    )


# Create database tables and run application
if __name__ == "__main__":
    

    with app.app_context():
        db.create_all()
        print("MySQL Database Connected Successfully!")
        print("Database tables created successfully!")

    app.run(debug=True)

