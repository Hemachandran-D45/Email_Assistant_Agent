# utils/hil_queue.py
import json
import os
import uuid
from typing import Dict, List, Any

HIL_FILE = "hil_pending.json"

def _load() -> List[Dict[str, Any]]:
    if not os.path.exists(HIL_FILE):
        return []
    with open(HIL_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def _save(data: List[Dict[str, Any]]) -> None:
    with open(HIL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def enqueue(email: Dict[str, Any], thread_id: str, draft: Dict[str, Any]) -> str:
    """Add a pending review item to the queue and return its id."""
    data = _load()
    item_id = str(uuid.uuid4())
    data.append({
        "id": item_id,
        "status": "pending",        # pending | approved | rejected | sent
        "email": email,             # {id, sender, subject, body}
        "thread_id": thread_id,
        "draft": draft,             # {reply, confidence}
        "history": {},              # reserved for future
    })
    _save(data)
    return item_id

def all_items() -> List[Dict[str, Any]]:
    return _load()

def update_item(item_id: str, **fields):
    data = _load()
    for it in data:
        if it["id"] == item_id:
            it.update(fields)
            break
    _save(data)

def replace_draft(item_id: str, reply: str, confidence: int | None = None):
    data = _load()
    for it in data:
        if it["id"] == item_id:
            it["draft"]["reply"] = reply
            if confidence is not None:
                it["draft"]["confidence"] = confidence
            break
    _save(data)

def remove_item(item_id: str):
    data = _load()
    data = [it for it in data if it["id"] != item_id]
    _save(data)
