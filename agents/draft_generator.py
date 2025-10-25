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
You are a professional email assistant. Write a clear, polite, and concise reply.

Input:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Context: {context}
Classification:

Category: {classification.get('category', 'General')}

Tone: {classification.get('tone', 'Neutral')}

Instructions:

Keep it between 4–7 sentences.

Maintain a professional, natural tone (not overly formal).

Be action-oriented — respond or request what’s needed clearly.

If you need information, include a short, bullet-style checklist.

Avoid filler phrases (“hope you’re well,” “kindly note,” etc.).

Write only the email body (no greetings or signatures).

Output:
Reply (only the email body):
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
