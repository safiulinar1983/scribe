from core.tools import Tool
from . import macos

def schema(props, required=[]): return {'type':'object','properties':props,'required':required}

def build_registry():
    from memory.manager import MemoryManager
    r=[]
    # Registry is populated by agent.py so memory methods can be bound there.
    return r

def register_macos(reg):
    S=lambda p,req=[]: schema(p,req)
    reg.register(Tool('calendar.find_events','Найти события календаря по части названия.',S({'query':{'type':'string'} }),macos.calendar_find))
    reg.register(Tool('calendar.create_event','Создать событие календаря. Дата должна быть строкой, распознаваемой macOS.',S({'title':{'type':'string'},'start':{'type':'string'},'end':{'type':'string'},'calendar':{'type':'string'}},['title','start','end']),macos.calendar_create))
    reg.register(Tool('calendar.delete_event','Удалить событие по UID. Требует подтверждения.',S({'uid':{'type':'string'}},['uid']),macos.calendar_delete,True))
    reg.register(Tool('reminders.find','Найти напоминания.',S({'query':{'type':'string'}}),macos.reminders_find))
    reg.register(Tool('reminders.create','Создать напоминание.',S({'name':{'type':'string'},'due_date':{'type':'string'},'list_name':{'type':'string'}},['name']),macos.reminders_create))
    reg.register(Tool('reminders.complete','Завершить напоминание.',S({'reminder_id':{'type':'string'}},['reminder_id']),macos.reminders_complete))
    reg.register(Tool('reminders.delete','Удалить напоминание. Требует подтверждения.',S({'reminder_id':{'type':'string'}},['reminder_id']),macos.reminders_delete,True))
    reg.register(Tool('notes.search','Найти заметки по названию.',S({'query':{'type':'string'}}),macos.notes_search))
    reg.register(Tool('notes.create','Создать заметку.',S({'title':{'type':'string'},'body':{'type':'string'},'folder':{'type':'string'}},['title','body']),macos.notes_create))
    reg.register(Tool('notes.append','Добавить текст в заметку.',S({'note_id':{'type':'string'},'text':{'type':'string'}},['note_id','text']),macos.notes_append))
    reg.register(Tool('notes.delete','Удалить заметку. Требует подтверждения.',S({'note_id':{'type':'string'}},['note_id']),macos.notes_delete,True))
