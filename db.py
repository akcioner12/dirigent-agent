"""
SQLite-хранилище очереди постов.
Статусы: pending -> approved/rejected -> published
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_channel TEXT,
                original_text TEXT,
                rewritten_text TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                published_at TEXT
            )
        """)


def add_post(source_channel: str, original_text: str, rewritten_text: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO posts (source_channel, original_text, rewritten_text, status, created_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (source_channel, original_text, rewritten_text, datetime.utcnow().isoformat()),
        )
        return cur.lastrowid


def get_post(post_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        return cur.fetchone()


def update_status(post_id: int, status: str):
    with get_conn() as conn:
        if status == "published":
            conn.execute(
                "UPDATE posts SET status = ?, published_at = ? WHERE id = ?",
                (status, datetime.utcnow().isoformat(), post_id),
            )
        else:
            conn.execute("UPDATE posts SET status = ? WHERE id = ?", (status, post_id))


def update_text(post_id: int, new_text: str):
    with get_conn() as conn:
        conn.execute("UPDATE posts SET rewritten_text = ? WHERE id = ?", (new_text, post_id))


def count_published_today() -> int:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE status = 'published' AND published_at LIKE ?",
            (f"{today}%",),
        )
        return cur.fetchone()[0]
