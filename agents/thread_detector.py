import uuid
from utils.chroma_db import similarity_search_with_score, add_email_to_index

class ThreadDetector:
    """
    Semantic thread detection using vector similarity.
    If most similar doc comes from the same sender and distance is small enough, reuse its thread_id.
    Otherwise, create a new one. Always store the email in the chosen thread.
    """
    def __init__(self, threshold: float = 0.3):
        # With MiniLM embeddings, distances ~0.2-0.4 indicate decent similarity
        self.threshold = threshold

    def detect_or_create_thread(self, email: dict) -> str:
        query = f"{email['sender']} {email['subject']} {email['body']}"
        results = similarity_search_with_score(query, k=1)

        thread_id = None
        if results:
            doc, score = results[0]
            meta = doc.metadata or {}
            if meta.get("sender") == email["sender"] and score <= self.threshold:
                thread_id = meta.get("thread_id")

        if not thread_id:
            thread_id = str(uuid.uuid4())

        add_email_to_index(email, thread_id)
        return thread_id
