"""Create or reset the local SalesPro administrator account.
Run from the backend folder: python create_admin.py
"""
from database import get_db, initialize_database
from werkzeug.security import generate_password_hash

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"
ADMIN_NAME = "SalesPro Administrator"

initialize_database()
db = get_db()
try:
    existing = db.execute("SELECT id FROM users WHERE LOWER(email)=LOWER(?)", (ADMIN_EMAIL,)).fetchone()
    password_hash = generate_password_hash(ADMIN_PASSWORD)
    if existing:
        db.execute(
            "UPDATE users SET name=?, full_name=?, password=?, role='admin', active=1 WHERE id=?",
            (ADMIN_NAME, ADMIN_NAME, password_hash, existing["id"])
        )
        action = "Updated existing account"
    else:
        db.execute(
            "INSERT INTO users (name, full_name, email, password, role, active) VALUES (?, ?, ?, ?, 'admin', 1)",
            (ADMIN_NAME, ADMIN_NAME, ADMIN_EMAIL, password_hash)
        )
        action = "Created new account"
    db.commit()
    print(f"{action} successfully.")
    print(f"Admin email: {ADMIN_EMAIL}")
    print(f"Admin password: {ADMIN_PASSWORD}")
    print("Now start the backend with: python app.py")
finally:
    db.close()
