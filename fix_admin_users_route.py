from pathlib import Path
import re

path = Path("app.py")
content = path.read_text(encoding="utf-8")

route_pattern = re.compile(
    r'(?ms)^@app\.route\("/admin/users"\)\s*\n'
    r'@login_required\s*\n'
    r'def admin_users\(\):.*?'
    r'(?=^@app\.route|^# Create database tables and run application|\Z)'
)

match = route_pattern.search(content)

if not match:
    print("ERROR: Admin users route was not found. No changes made.")
    raise SystemExit

route_code = match.group(0).strip() + "\n\n"
content = content[:match.start()] + content[match.end():]

marker = "# Create database tables and run application"

if marker not in content:
    print("ERROR: Main application marker not found. No changes made.")
    raise SystemExit

if route_pattern.search(content):
    print("ERROR: Duplicate route detected. No changes made.")
    raise SystemExit

content = content.replace(
    marker,
    route_code + marker,
    1
)

path.write_text(content, encoding="utf-8")

print("SUCCESS! Admin users route moved before app.run().")
