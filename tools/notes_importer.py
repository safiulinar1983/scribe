from __future__ import annotations
from .macos import notes_export_all
from memory.manager import MemoryManager

class NotesImporter:
    def __init__(self,memory:MemoryManager): self.memory=memory
    def sync(self):
        raw=notes_export_all(); count=0; changed=0
        if not raw: return {'notes':0,'changed':0}
        for record in raw.split('<<<NOTE>>>'):
            if not record.strip(): continue
            parts=record.split('<<<F>>>',3)
            if len(parts)!=4: continue
            note_id,folder_id,title,body=parts
            if self.memory.note_is_changed(note_id,body):
                changed+=1
                self.memory.note_index(note_id,folder_id,title,'',body)
                # First version does not automatically invent memories from arbitrary note text.
                # It only indexes metadata; explicit facts can later be saved through the Memory API.
            count+=1
        return {'notes':count,'changed':changed}
