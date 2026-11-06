from pathlib import Path

path = Path("app.py")
content = path.read_text(encoding="utf-8")

old = '''elif user.role == "recruiter":
                return redirect(url_for("recruiter_dashboard"))

            else:'''

new = '''elif user.role == "recruiter":
                return redirect(url_for("recruiter_dashboard"))

            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            else:'''

count = content.count(old)

if count == 1:
    content = content.replace(old, new, 1)
    path.write_text(content, encoding="utf-8")
    print("SUCCESS! Admin login redirect added.")
elif count == 0:
    print("The expected login code was not found. No changes made.")
else:
    print("Multiple matches found. No changes made.")
