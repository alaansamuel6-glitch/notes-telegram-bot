import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"
NOTES_DB_NAME = "notes.db"


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
        conn.commit()

    with sqlite3.connect(NOTES_DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


def add_reminder(user_id: int, text: str, remind_at: datetime) -> int:
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute(
            "INSERT INTO reminders (user_id, text, remind_at) VALUES (?, ?, ?)",
            (user_id, text, remind_at.strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
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
        conn.commit()


def mark_done(reminder_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE reminders SET done = 1 WHERE id = ?", (reminder_id,))
        conn.commit()


def add_note(user_id: int, text: str) -> int:
    with sqlite3.connect(NOTES_DB_NAME) as conn:
        cur = conn.execute(
            "INSERT INTO notes (user_id, text) VALUES (?, ?)",
            (user_id, text)
        )
        conn.commit()
        return cur.lastrowid


def get_notes(user_id: int):
    with sqlite3.connect(NOTES_DB_NAME) as conn:
        return conn.execute(
            "SELECT id, text FROM notes WHERE user_id = ? ORDER BY id",
            (user_id,)
        ).fetchall()


def delete_note(note_id: int):
    with sqlite3.connect(NOTES_DB_NAME) as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()


def get_stats(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        active = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id = ? AND done = 0",
            (user_id,)
        ).fetchone()[0]

        done = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id = ? AND done = 1",
            (user_id,)
        ).fetchone()[0]

        today = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id = ? AND done = 0 AND date(remind_at) = date('now', 'localtime')",
            (user_id,)
        ).fetchone()[0]

        week = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE user_id = ? AND done = 0 AND date(remind_at) BETWEEN date('now','localtime') AND date('now','localtime','+7 days')",
            (user_id,)
        ).fetchone()[0]

        nearest = conn.execute(
            "SELECT text, remind_at FROM reminders WHERE user_id = ? AND done = 0 ORDER BY remind_at LIMIT 1",
            (user_id,)
        ).fetchone()

    with sqlite3.connect(NOTES_DB_NAME) as conn:
        notes = conn.execute(
            "SELECT COUNT(*) FROM notes WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

    return {
        "active": active,
        "done": done,
        "today": today,
        "week": week,
        "nearest": nearest,
        "notes": notes,
    }
