import sqlite3
from datetime import datetime

DATABASE_NAME = "chatbot.db"


# ----------------------------------------------------
# Database Connection
# ----------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------------------------------
# Create Database
# ----------------------------------------------------
def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- Users ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        created_at TEXT
    )
    """)

    # ---------------- Conversations ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        title TEXT,

        created_at TEXT,

        updated_at TEXT,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
    )
    """)

    # ---------------- Messages ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        conversation_id INTEGER NOT NULL,

        sender TEXT NOT NULL,

        message TEXT NOT NULL,

        intent TEXT,

        source TEXT,

        timestamp TEXT,

        FOREIGN KEY(conversation_id)
        REFERENCES conversations(id)
    )
    """)

    conn.commit()
    conn.close()


# ----------------------------------------------------
# Conversation
# ----------------------------------------------------

def create_conversation(user_id, title="New Chat"):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO conversations
    (user_id,title,created_at,updated_at)
    VALUES(?,?,?,?)
    """,
    (
        user_id,
        title,
        now,
        now
    ))

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


# ----------------------------------------------------
# Save Message
# ----------------------------------------------------

def save_message(
        conversation_id,
        sender,
        message,
        intent="",
        source=""
):

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO messages
        (
            conversation_id,
            sender,
            message,
            intent,
            source,
            timestamp
        )
        VALUES(?,?,?,?,?,?)
    """,
    (
        conversation_id,
        sender,
        message,
        intent,
        source,
        now
    ))

    # Update conversation time
    cursor.execute("""
        UPDATE conversations
        SET updated_at=?
        WHERE id=?
    """,
    (
        now,
        conversation_id
    ))

    # ---------- NEW ----------
    # If this is the first user message,
    # use it as the conversation title.

    if sender == "user":

        cursor.execute("""
            SELECT COUNT(*)
            FROM messages
            WHERE conversation_id=?
              AND sender='user'
        """, (conversation_id,))

        count = cursor.fetchone()[0]

        if count == 1:

            title = message[:40]

            cursor.execute("""
                UPDATE conversations
                SET title=?
                WHERE id=?
            """, (title, conversation_id))

    conn.commit()
    conn.close()


# ----------------------------------------------------
# Get Conversations
# ----------------------------------------------------

def get_conversations(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM conversations
    WHERE user_id=?
    ORDER BY updated_at DESC
    """,
    (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------------------
# Get Messages
# ----------------------------------------------------

def get_messages(conversation_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM messages
    WHERE conversation_id=?
    ORDER BY id ASC
    """,
    (conversation_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# ----------------------------------------------------
# Dashboard Stats
# ----------------------------------------------------

def get_dashboard_stats(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM conversations
    WHERE user_id=?
    """,
    (user_id,)
    )

    total_conversations = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM messages
    WHERE conversation_id IN
    (
        SELECT id
        FROM conversations
        WHERE user_id=?
    )
    """,
    (user_id,)
    )

    total_messages = cursor.fetchone()[0]

    conn.close()

    return {
        "conversations": total_conversations,
        "messages": total_messages
    }

def get_recent_messages(conversation_id, limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, message
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (conversation_id, limit))

    rows = cursor.fetchall()

    conn.close()

    return list(reversed(rows))