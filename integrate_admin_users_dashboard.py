from pathlib import Path
import re

# Update app.py
app_path = Path("app.py")
app_text = app_path.read_text(encoding="utf-8")

pattern = r'return render_template\(\s*"admin_dashboard\.html".*?\n\s*\)'

replacement = '''users = User.query.order_by(User.id.desc()).all()

    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()

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
        inactive_users=inactive_users
    )'''

route_start = app_text.find('@app.route("/admin-dashboard")')
if route_start == -1:
    raise SystemExit("Admin dashboard route not found in app.py.")

route_end = app_text.find('\n@app.route(', route_start + 1)
if route_end == -1:
    route_end = len(app_text)

route = app_text[route_start:route_end]

if "users=users" not in route:
    updated_route, count = re.subn(pattern, replacement, route, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("Could not safely update the admin route. No changes saved.")
    app_text = app_text[:route_start] + updated_route + app_text[route_end:]
    app_path.write_text(app_text, encoding="utf-8")

# Update admin dashboard template
template_path = Path("templates/admin_dashboard.html")
html = template_path.read_text(encoding="utf-8")

marker = "    <!-- MANAGEMENT CENTER -->"

section = '''
    <!-- USER MANAGEMENT INSIDE ADMIN DASHBOARD -->
    <section id="user-management">

        <h3 class="section-title">
            <i class="fa-solid fa-users-gear me-2" style="color:#4267d5;"></i>
            User Management
        </h3>

        <div class="quick-info" style="margin-top:0;">

            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4">
                <div>
                    <h5 style="font-weight:800; margin-bottom:5px;">Registered Users</h5>
                    <small style="color:#8791a6;">Manage and monitor platform accounts</small>
                </div>

                <div class="d-flex gap-2 flex-wrap">
                    <span class="badge rounded-pill text-bg-success p-2">
                        Active: {{ active_users }}
                    </span>
                    <span class="badge rounded-pill text-bg-secondary p-2">
                        Inactive: {{ inactive_users }}
                    </span>
                </div>
            </div>

            <input type="text" id="userSearch"
                   class="form-control mb-3"
                   placeholder="Search by name or email..."
                   style="max-width:400px; padding:12px;">

            <div class="table-responsive">
                <table class="table align-middle">
                    <thead style="background:#f3f5fb;">
                        <tr>
                            <th>User</th>
                            <th>User ID</th>
                            <th>Role</th>
                            <th>Account Status</th>
                        </tr>
                    </thead>
                    <tbody id="userTableBody">
                        {% for user in users %}
                        <tr class="user-row">
                            <td>
                                <strong>{{ user.full_name }}</strong><br>
                                <small class="text-muted">{{ user.email }}</small>
                            </td>
                            <td>#{{ user.id }}</td>
                            <td>
                                {% if user.role == 'admin' %}
                                    <span class="badge rounded-pill text-bg-primary">Admin</span>
                                {% elif user.role == 'recruiter' %}
                                    <span class="badge rounded-pill text-bg-info">Recruiter</span>
                                {% else %}
                                    <span class="badge rounded-pill text-bg-secondary">Job Seeker</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if user.is_active %}
                                    <span class="badge rounded-pill text-bg-success">Active</span>
                                {% else %}
                                    <span class="badge rounded-pill text-bg-danger">Inactive</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4" class="text-center text-muted">
                                No registered users found.
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </section>

'''

if 'id="user-management"' not in html:
    if marker not in html:
        raise SystemExit("Management Center section marker not found in admin_dashboard.html.")
    html = html.replace(marker, section + marker, 1)
    template_path.write_text(html, encoding="utf-8")

# Add search behavior
if 'id="userSearch"' in html and 'userSearch.addEventListener' not in html:
    search_script = '''
<script>
document.addEventListener("DOMContentLoaded", function () {
    const search = document.getElementById("userSearch");
    if (!search) return;

    search.addEventListener("input", function () {
        const value = this.value.toLowerCase();

        document.querySelectorAll("#userTableBody .user-row").forEach(function (row) {
            row.style.display = row.innerText.toLowerCase().includes(value) ? "" : "none";
        });
    });
});
</script>
'''
    html = html.replace("</body>", search_script + "\\n</body>")
    template_path.write_text(html, encoding="utf-8")

print("SUCCESS! User Management is now included in the main Admin Dashboard.")
print("Updated: app.py and templates/admin_dashboard.html")
