import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class ConversationManager:
    def __init__(self, path):
        self.path=Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self._init()
    def _conn(self):
        c=sqlite3.connect(self.path); c.execute('PRAGMA journal_mode=WAL'); return c
    def _init(self):
        with self._conn() as c:
            c.execute('CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY, created_at TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, conversation_id INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)')
    def new(self):
        now=datetime.now(timezone.utc).isoformat();
        with self._conn() as c:
            cur=c.execute('INSERT INTO conversations(created_at) VALUES(?)',(now,)); return cur.lastrowid
    def add(self,cid,role,content):
        with self._conn() as c: c.execute('INSERT INTO messages(conversation_id,role,content,created_at) VALUES(?,?,?,?)',(cid,role,content,datetime.now(timezone.utc).isoformat()))
