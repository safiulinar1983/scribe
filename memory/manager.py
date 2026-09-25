from __future__ import annotations
from datetime import datetime, timezone
import hashlib, shutil
from pathlib import Path
from .database import Database

class MemoryManager:
    def __init__(self,path): self.db=Database(path)
    def remember(self,content,category='other',source='user',source_id=None,importance=5,explicit=1):
        now=datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c:
            existing=c.execute('SELECT * FROM memories WHERE content=? AND source=? AND COALESCE(source_id,\'\')=COALESCE(?,\'\')',(content,source,source_id)).fetchone()
            if existing: return dict(existing)
            cur=c.execute('INSERT INTO memories(content,category,source,source_id,created_at,updated_at,importance,explicit) VALUES(?,?,?,?,?,?,?,?)',(content,category,source,source_id,now,now,importance,explicit))
            return dict(c.execute('SELECT * FROM memories WHERE id=?',(cur.lastrowid,)).fetchone())
    def search(self,query,limit=10):
        words=[w.lower() for w in query.split() if len(w)>2]
        if not words: return []
        with self.db.connect() as c:
            clauses=[]; args=[]
            for w in words: clauses.append('lower(content) LIKE ?'); args.append('%'+w+'%')
            return [dict(x) for x in c.execute('SELECT * FROM memories WHERE '+' OR '.join(clauses)+' ORDER BY importance DESC,updated_at DESC LIMIT ?',args+[limit])]
    def update(self,id,**fields):
        allowed={'content','category','source','source_id','importance','needs_review'}; fields={k:v for k,v in fields.items() if k in allowed}
        fields['updated_at']=datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c:
            if fields:
                c.execute('UPDATE memories SET '+','.join(f'{k}=?' for k in fields)+' WHERE id=?',list(fields.values())+[id])
            row=c.execute('SELECT * FROM memories WHERE id=?',(id,)).fetchone(); return dict(row) if row else None
    def forget(self,id):
        with self.db.connect() as c: c.execute('DELETE FROM memories WHERE id=?',(id,))
    def list(self,limit=100):
        with self.db.connect() as c:return [dict(x) for x in c.execute('SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?',(limit,))]
    def clear(self,backup_dir):
        backup_dir=Path(backup_dir); backup_dir.mkdir(parents=True,exist_ok=True)
        stamp=datetime.now().strftime('%Y-%m-%d_%H-%M-%S'); dest=backup_dir/f'memory_{stamp}.db'
        with self.db.connect() as c:
            dst=Database(str(dest)).connect(); c.backup(dst); dst.close()
            c.execute('DELETE FROM memories')
            return str(dest)
    def note_index(self,note_id,folder_id,title,last_modified,content):
        h=hashlib.sha256(content.encode('utf-8')).hexdigest(); now=datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c:
            c.execute('''INSERT INTO note_index(note_id,folder_id,title,last_modified,content_hash,indexed_at) VALUES(?,?,?,?,?,?)
                         ON CONFLICT(note_id) DO UPDATE SET folder_id=excluded.folder_id,title=excluded.title,last_modified=excluded.last_modified,content_hash=excluded.content_hash,indexed_at=excluded.indexed_at''',(note_id,folder_id,title,last_modified,h,now))
    def note_is_changed(self,note_id,content,last_modified=None):
        h=hashlib.sha256(content.encode('utf-8')).hexdigest()
        with self.db.connect() as c:
            row=c.execute('SELECT content_hash,last_modified FROM note_index WHERE note_id=?',(note_id,)).fetchone()
            return row is None or row['content_hash']!=h or (last_modified is not None and row['last_modified']!=last_modified)
