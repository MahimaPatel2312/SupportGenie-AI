import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = "chatbot.db"


# ---------------------------------------
# Register New User
# ---------------------------------------
def register_user(name, email, password):

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,)
    )

    if cursor.fetchone():
        conn.close()
        return False, "Email already registered."

    # Hash password
    hashed_password = generate_password_hash(password)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO users
        (name, email, password, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        hashed_password,
        current_time
    ))

    conn.commit()
    conn.close()

    return True, "Registration successful."


# ---------------------------------------
# Login User
# ---------------------------------------
def login_user(email, password):

    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    # Verify password
    if check_password_hash(user["password"], password):
        return dict(user)

    return None