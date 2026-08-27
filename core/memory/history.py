"""
Action History Logger

Logs all actions taken by Sprout for auditing and memory
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from config import memory_config

class ActionHistory:
    """Logs and retrieves action history"""

    def __init__(self):
        self.db_path = memory_config.action_log_path
        self._init_db()

    def _init_db(self):
        """Initialize the action log database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                intent_type TEXT,
                risk_level TEXT,
                action TEXT,
                target TEXT,
                permission_granted BOOLEAN,
                success BOOLEAN,
                result TEXT
            )
        """)

        conn.commit()
        conn.close()

    def log_action(self, intent_type: str, risk_level: str, action: str,
                   target: str, permission_granted: bool, success: bool,
                   result: str):
        """Log an action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO actions (timestamp, intent_type, risk_level, action,
                               target, permission_granted, success, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now(), intent_type, risk_level, action, target,
              permission_granted, success, result))

        conn.commit()
        conn.close()

    def get_recent_actions(self, limit: int = 20) -> List[Dict]:
        """Get recent actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, intent_type, risk_level, action, target,
                   permission_granted, success, result
            FROM actions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        actions = []
        for row in cursor.fetchall():
            actions.append({
                "timestamp": row[0],
                "intent_type": row[1],
                "risk_level": row[2],
                "action": row[3],
                "target": row[4],
                "permission_granted": bool(row[5]),
                "success": bool(row[6]),
                "result": row[7]
            })

        conn.close()
        return actions

    def search_actions(self, query: str, limit: int = 10) -> List[Dict]:
        """Search actions by query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, intent_type, action, target, success, result
            FROM actions
            WHERE action LIKE ? OR target LIKE ? OR result LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))

        actions = []
        for row in cursor.fetchall():
            actions.append({
                "timestamp": row[0],
                "intent_type": row[1],
                "action": row[2],
                "target": row[3],
                "success": bool(row[4]),
                "result": row[5]
            })

        conn.close()
        return actions
