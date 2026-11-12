import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                done INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)

def add_reminder(user_id: int, text: str, remind_at: datetime) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "INSERT INTO reminders (user_id, text, remind_at) VALUES (?, ?, ?)",
            (user_id, text, remind_at.strftime("%Y-%m-%d %H:%M"))
        )
        return cur.lastrowid

def get_user_reminders(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT id, text, remind_at FROM reminders WHERE user_id = ? AND done = 0 ORDER BY remind_at",
            (user_id,)
        ).fetchall()

def get_all_pending():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT id, user_id, text, remind_at FROM reminders WHERE done = 0"
        ).fetchall()

def delete_reminder(reminder_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

def add_note(user_id: int, text: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))

def get_notes(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT id, text FROM notes WHERE user_id = ?", (user_id,)).fetchall()

def delete_note(note_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
