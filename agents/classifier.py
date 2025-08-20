import json
from utils.llm_loader import load_llm
from utils.types import Classification

class ClassifierAgent:
    def __init__(self):
        self.llm = load_llm()

    def classify(self, email: dict) -> Classification:
        prompt = f"""
You are an email triage assistant. Return ONLY JSON with keys: category, tone.
- category must be one of: ["spam", "urgent", "quick_reply", "normal"]
- tone should be a single word such as: "angry", "neutral", "happy", "frustrated", "formal", "informal"

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}
"""
        resp = self.llm.invoke(prompt)
        text = resp.content if hasattr(resp, "content") else str(resp)

        try:
            data = json.loads(text)
            category = str(data.get("category", "normal")).lower()
            tone = str(data.get("tone", "neutral")).lower()
        except Exception:
            # naive fallback
            body = email["body"].lower()
            if "unsubscribe" in body or "lottery" in body or "win money" in body:
                category = "spam"
            elif "asap" in body or "urgent" in body or "immediately" in body:
                category = "urgent"
            elif len(body) < 220:
                category = "quick_reply"
            else:
                category = "normal"
            tone = "neutral"

        return {"category": category, "tone": tone, "confidence": 0.7}
