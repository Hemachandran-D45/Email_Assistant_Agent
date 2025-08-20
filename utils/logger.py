import datetime

def log(msg: str):
    print(f"[{datetime.datetime.now().isoformat()}] {msg}")

def log_event(event: str, payload: dict | None = None, **kwargs):
    log(f"EVENT={event} | PAYLOAD={payload or {}} | META={kwargs}")

def log_classification(email_id, thread_id, category, tone, raw):
    log(f"📊 Classification | Email {email_id} | Thread {thread_id} | Category={category}, Tone={tone}, Raw={raw}")

def log_draft(email_id, thread_id, reply, confidence, history_hits):
    snippet = (reply or "")[:120].replace("\n", " ")
    log(f"✍️ Draft | Email {email_id} | Thread {thread_id} | Conf={confidence} | Hits={history_hits} | {snippet}...")

def log_send(email_id, thread_id, to_email, subject):
    log(f"📤 Sent | Email {email_id} | Thread {thread_id} | To={to_email} | Subject={subject}")

def log_hil_queued(email_id, thread_id, confidence):
    log(f"🧑‍⚖️ HIL Queue | Email {email_id} | Thread {thread_id} | Conf={confidence}")
