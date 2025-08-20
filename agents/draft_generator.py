from utils.llm_loader import load_llm
from utils.chroma_db import similarity_search
from agents.thread_detector import ThreadDetector

class DraftGeneratorAgent:
    def __init__(self):
        self.llm = load_llm()
        self.thread_detector = ThreadDetector()

    def generate_reply(self, email: dict, classification: dict):
        # Decide thread (also stores this email)
        thread_id = self.thread_detector.detect_or_create_thread(email)

        # Prefer thread-level context
        hits = similarity_search(email["body"], k=3, _filter={"thread_id": thread_id})

        # Fallback to sender-wide if no thread context
        if not hits:
            hits = similarity_search(email["body"], k=3, _filter={"sender": email["sender"]})

        context = "\n\n".join([d.page_content for d in hits]) if hits else "No relevant history."

        prompt = f"""
You are an AI email assistant. Draft a concise, polite, professional reply.

Incoming Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Classification:
- Category: {classification.get('category','normal')}
- Tone: {classification.get('tone','neutral')}

Relevant Past Emails (context):
{context}

Constraints:
- Be concise (5-8 sentences).
- If asking for info, use a short checklist.
- Avoid generic fluff; be specific and helpful.

Reply (only the email body, no headers or signatures):
"""
        resp = self.llm.invoke(prompt)
        reply = resp.content if hasattr(resp, "content") else str(resp)

        confidence = 8 if hits else 6
        if classification.get("category") == "urgent":
            confidence = max(confidence - 1, 5)

        return {
            "reply": reply.strip(),
            "confidence": confidence,
            "history_hits": len(hits) if hits else 0,
            "thread_id": thread_id,
        }
