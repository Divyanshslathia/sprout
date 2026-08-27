"""
Session Memory

Stores conversation history and short-term context using SQLite
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import memory_config

class SessionMemory:
    """Manages conversation sessions and history"""

    def __init__(self):
        self.db_path = memory_config.session_db_path
        self._init_db()

    def _init_db(self):
        """Initialize the session database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                content TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_session(self) -> int:
        """Create a new session and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO sessions (started_at, active) VALUES (?, 1)",
                      (datetime.now(),))
        session_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return session_id

    def add_message(self, session_id: int, role: str, content: str):
        """Add a message to the session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (session_id, timestamp, role, content)
            VALUES (?, ?, ?, ?)
        """, (session_id, datetime.now(), role, content))

        conn.commit()
        conn.close()

    def get_session_history(self, session_id: int, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "timestamp": row[0],
                "role": row[1],
                "content": row[2]
            })

        conn.close()
        return list(reversed(messages))

    def end_session(self, session_id: int):
        """Mark a session as ended"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE sessions
            SET ended_at = ?, active = 0
            WHERE id = ?
        """, (datetime.now(), session_id))

        conn.commit()
        conn.close()

    def get_active_session(self) -> Optional[int]:
        """Get the current active session ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM sessions
            WHERE active = 1
            ORDER BY started_at DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None
