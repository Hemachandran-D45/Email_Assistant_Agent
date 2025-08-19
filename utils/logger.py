import datetime
import json

def log(msg: str):
    """Base logger function with timestamp."""
    print(f"[{datetime.datetime.now().isoformat()}] {msg}")

def log_classification(email_id, thread_id, category, tone, raw):
    """Log when an email is classified."""
    log(
        f"📊 Classification | Email={email_id} | Thread={thread_id} | "
        f"Category={category}, Tone={tone}, Raw={json.dumps(raw)}"
    )

def log_draft(email_id, thread_id, reply, confidence, history_hits):
    """Log when a draft reply is generated."""
    preview = reply[:80].replace("\n", " ") + ("..." if len(reply) > 80 else "")
    log(
        f"✍️ Draft | Email={email_id} | Thread={thread_id} | "
        f"Confidence={confidence} | HistoryHits={history_hits} | ReplyPreview='{preview}'"
    )

def log_send(email_id, thread_id, to_email, subject):
    """Log when an email is actually sent."""
    log(
        f"📤 Sent | Email={email_id} | Thread={thread_id} | "
        f"To={to_email} | Subject='{subject}'"
    )

def log_hil_queued(email_id, thread_id, confidence):
    """Log when an email is queued for human-in-the-loop review."""
    log(
        f"🧑‍💻 Human-in-loop | Email={email_id} | Thread={thread_id} | "
        f"Confidence={confidence}"
    )

def log_event(event_type: str, details: dict):
    """General-purpose event logging (for UI or debugging)."""
    log(f"📝 Event | Type={event_type} | Details={json.dumps(details)}")
