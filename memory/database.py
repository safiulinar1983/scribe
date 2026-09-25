import sqlite3
from pathlib import Path

SCHEMA_VERSION=2
class Database:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.migrate()
    def connect(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA foreign_keys=ON'); return c
    def migrate(self):
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL)')
            row=c.execute('SELECT version FROM schema_version').fetchone()
            v=row[0] if row else 0
            if v<1:
                c.execute('''CREATE TABLE IF NOT EXISTS memories(
                    id INTEGER PRIMARY KEY, content TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'other',
                    source TEXT NOT NULL DEFAULT 'user', source_id TEXT, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, importance INTEGER NOT NULL DEFAULT 5, explicit INTEGER NOT NULL DEFAULT 1,
                    needs_review INTEGER NOT NULL DEFAULT 0)''')
                c.execute('CREATE INDEX IF NOT EXISTS idx_memories_content ON memories(content)')
                c.execute('CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source,source_id)')
                c.execute('INSERT INTO schema_version VALUES(1)')
                v=1
            if v<2:
                c.execute('CREATE TABLE IF NOT EXISTS note_index(note_id TEXT PRIMARY KEY, folder_id TEXT, title TEXT, last_modified TEXT, content_hash TEXT NOT NULL, indexed_at TEXT NOT NULL)')
                c.execute('UPDATE schema_version SET version=2')
