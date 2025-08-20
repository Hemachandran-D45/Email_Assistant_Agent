import os, json, uuid

QUEUE_FILE = os.path.join(os.getcwd(), "hil_queue.json")

def _load():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(items):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def enqueue(email: dict, draft: dict, thread_id: str):
    items = _load()
    item = {"id": str(uuid.uuid4()), "email": email, "draft": draft, "thread_id": thread_id, "status": "pending"}
    items.append(item)
    _save(items)
    return item["id"]

def all_items():
    return _load()

def update_item(item_id: str, **fields):
    items = _load()
    for it in items:
        if it["id"] == item_id:
            it.update(fields)
            _save(items)
            return True
    return False

def get_item(item_id: str):
    for it in _load():
        if it["id"] == item_id:
            return it
    return None

def replace_draft(item_id: str, new_text: str):
    it = get_item(item_id)
    if not it:
        return False
    it["draft"]["reply"] = new_text
    items = _load()
    for i, obj in enumerate(items):
        if obj["id"] == item_id:
            items[i] = it
            break
    _save(items)
    return True

def remove_item(item_id: str):
    items = _load()
    items = [it for it in items if it["id"] != item_id]
    _save(items)
