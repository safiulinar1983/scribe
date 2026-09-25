from __future__ import annotations
import subprocess, json, shlex

def run_osascript(script: str) -> str:
    p=subprocess.run(['osascript','-e',script],capture_output=True,text=True,timeout=30)
    if p.returncode: raise RuntimeError(p.stderr.strip() or 'osascript failed')
    return p.stdout.strip()

def _q(s): return json.dumps(str(s),ensure_ascii=False)

def _ensure_calendar_running():
    p = subprocess.run(
        ["pgrep", "-x", "Calendar"],
        capture_output=True,
        text=True
    )
    if p.returncode != 0:
        subprocess.run(["open", "-gja", "Calendar"], check=True)
        import time
        time.sleep(2)


def calendar_find(query=''):
    _ensure_calendar_running()
    script=f'''tell application "Calendar"
set out to {{}}
repeat with c in calendars
repeat with e in (every event of c whose summary contains {_q(query)})
set end of out to (summary of e & " | " & ((start date of e) as string) & " | " & (uid of e))
end repeat
end repeat
return out as string
end tell'''
    return run_osascript(script)

def calendar_create(title, start, end, calendar='Домашний'):
    _ensure_calendar_running()
    from datetime import datetime

    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)

    script = f'''tell application "Calendar"
set c to calendar {_q(calendar)}
tell c
set startDate to current date
set year of startDate to {start_dt.year}
set month of startDate to {start_dt.month}
set day of startDate to {start_dt.day}
set hours of startDate to {start_dt.hour}
set minutes of startDate to {start_dt.minute}
set seconds of startDate to {start_dt.second}

set endDate to current date
set year of endDate to {end_dt.year}
set month of endDate to {end_dt.month}
set day of endDate to {end_dt.day}
set hours of endDate to {end_dt.hour}
set minutes of endDate to {end_dt.minute}
set seconds of endDate to {end_dt.second}

set e to make new event with properties {{summary:{_q(title)}, start date:startDate, end date:endDate}}
return uid of e
end tell
end tell'''
    return run_osascript(script)

def calendar_delete(uid):
    _ensure_calendar_running()
    script=f'''tell application "Calendar"
repeat with c in calendars
    tell c
        set eventCount to count of events
        repeat with i from 1 to eventCount
            set e to event i
            if (uid of e) is {_q(uid)} then
                delete e
                return "deleted"
            end if
        end repeat
    end tell
end repeat
error "event not found"
end tell'''
    return run_osascript(script)

def reminders_find(query=''):
    script=f'''tell application "Reminders"
set out to {{}}
repeat with l in lists
repeat with r in (every reminder of l whose name contains {_q(query)})
set end of out to (name of r & " | " & (id of r))
end repeat
end repeat
return out as string
end tell'''
    return run_osascript(script)

def reminders_create(name, due_date=None, list_name='Reminders'):
    due = '' if not due_date else f', due date:date {_q(due_date)}'
    script=f'''tell application "Reminders"
set l to list {_q(list_name)}
tell l
set r to make new reminder with properties {{name:{_q(name)}{due}}}
return id of r
end tell
end tell'''
    return run_osascript(script)

def reminders_complete(reminder_id):
    script=f'''tell application "Reminders"
repeat with l in lists
try
set r to some reminder of l whose id is {_q(reminder_id)}
set completed of r to true
return "completed"
end try
end repeat
error "reminder not found"
end tell'''
    return run_osascript(script)

def reminders_delete(reminder_id):
    script=f'''tell application "Reminders"
repeat with l in lists
try
set r to some reminder of l whose id is {_q(reminder_id)}
delete r
return "deleted"
end try
end repeat
error "reminder not found"
end tell'''
    return run_osascript(script)

def notes_search(query=''):
    script=f'''tell application "Notes"
set out to {{}}
repeat with a in accounts
repeat with n in (every note of a whose name contains {_q(query)})
set end of out to (name of n & " | " & (id of n))
end repeat
end repeat
return out as string
end tell'''
    return run_osascript(script)

def notes_create(title, body, folder='Notes'):
    script=f'''tell application "Notes"
set f to folder {_q(folder)}
make new note at f with properties {{name:{_q(title)}, body:{_q(body)}}}
return "created"
end tell'''
    return run_osascript(script)

def notes_append(note_id, text):
    script=f'''tell application "Notes"
repeat with a in accounts
try
set n to some note of a whose id is {_q(note_id)}
set body of n to (body of n & "<br>" & {_q(text)})
return "updated"
end try
end repeat
error "note not found"
end tell'''
    return run_osascript(script)

def notes_delete(note_id):
    script=f'''tell application "Notes"
repeat with a in accounts
try
set n to some note of a whose id is {_q(note_id)}
delete n
return "deleted"
end try
end repeat
error "note not found"
end tell'''
    return run_osascript(script)

def notes_export_all():
    # Read-only importer; returns JSON-ish records from AppleScript.
    script='''tell application "Notes"
set oldDelims to AppleScript's text item delimiters
set AppleScript's text item delimiters to "<<<NOTE>>>"
set out to ""
repeat with a in accounts
repeat with f in folders of a
repeat with n in notes of f
set out to out & (id of n) & "<<<F>>>" & (id of f) & "<<<F>>>" & (name of n) & "<<<F>>>" & (body of n) & "<<<NOTE>>>"
end repeat
end repeat
end repeat
set AppleScript's text item delimiters to oldDelims
return out
end tell'''
    return run_osascript(script)
