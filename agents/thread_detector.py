import uuid
from utils.chroma_db import get_email_collection

class ThreadDetector:
    def __init__(self):
        self.collection = get_email_collection()

    def detect_or_create_thread(self, sender: str, body: str):
        results = self.collection.query(query_texts=[body], n_results=1)
        if results and results["documents"]:
            meta = results["metadatas"][0][0]
            if "thread_id" in meta:
                return meta["thread_id"]

        thread_id = str(uuid.uuid4())
        self.collection.add(
            documents=[body],
            metadatas=[{"sender": sender, "thread_id": thread_id}],
            ids=[str(uuid.uuid4())]
        )
        return thread_id
