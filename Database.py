import sqlite3
import hashlib
import os

DB_PATH = "chatbot.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            created   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            title      TEXT DEFAULT 'New Chat',
            created    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL REFERENCES sessions(id),
            role       TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content    TEXT NOT NULL,
            created    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ── USER ──────────────────────────────────────────────────────────────────────
def create_user(username: str, password: str):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_pw(password))
        )
        conn.commit()
        return True, "Account created."
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    finally:
        conn.close()

def verify_user(username: str, password: str):
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return row["id"] if row else None

# ── SESSION ───────────────────────────────────────────────────────────────────
def create_session(user_id: int) -> int:
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO sessions (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid

def get_sessions(user_id: int):
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, s.title, s.created,
               COUNT(m.id) as msg_count
        FROM sessions s
        LEFT JOIN messages m ON m.session_id = s.id
        WHERE s.user_id = ?
        GROUP BY s.id
        ORDER BY s.created DESC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_session(session_id: int, user_id: int):
    conn = get_db()
    conn.execute(
        "DELETE FROM messages WHERE session_id=?", (session_id,)
    )
    conn.execute(
        "DELETE FROM sessions WHERE id=? AND user_id=?", (session_id, user_id)
    )
    conn.commit()
    conn.close()

def update_session_title(session_id: int, title: str):
    conn = get_db()
    conn.execute(
        "UPDATE sessions SET title=? WHERE id=?", (title[:60], session_id)
    )
    conn.commit()
    conn.close()

# ── MESSAGES ──────────────────────────────────────────────────────────────────
def add_message(session_id: int, role: str, content: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_messages(session_id: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content, created FROM messages WHERE session_id=? ORDER BY id",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def session_belongs_to(session_id: int, user_id: int) -> bool:
    conn = get_db()
    row = conn.execute(
        "SELECT 1 FROM sessions WHERE id=? AND user_id=?", (session_id, user_id)
    ).fetchone()
    conn.close()
    return row is not None