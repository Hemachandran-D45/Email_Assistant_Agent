from langchain.prompts import PromptTemplate
from utils.llm_loader import llm
from utils.chroma_db import get_email_collection

class DraftGeneratorAgent:
    def __init__(self):
        self.collection = get_email_collection()
        self.prompt = PromptTemplate(
            input_variables=["email_body", "history"],
            template="""
You are an email assistant. Write a **polite and concise reply** to the email below.
If there is relevant history, include proper context.

Email:
{email_body}

Conversation History:
{history}

Reply in a helpful and professional tone.
Also provide a confidence score from 1-10 about how certain you are.

Format:
REPLY: <your reply>
CONFIDENCE: <number>
            """
        )

    def generate_draft(self, email, thread_id):
        results = self.collection.query(query_texts=[email["body"]], n_results=3)
        history = "\n".join(doc for docs in results.get("documents", []) for doc in docs) if results else "No history."

        formatted_prompt = self.prompt.format(email_body=email["body"], history=history)
        response = llm.predict(formatted_prompt)

        reply_text, confidence_score = "", 5
        for line in response.split("\n"):
            if line.startswith("REPLY:"):
                reply_text = line.replace("REPLY:", "").strip()
            if line.startswith("CONFIDENCE:"):
                try:
                    confidence_score = int(line.replace("CONFIDENCE:", "").strip())
                except:
                    confidence_score = 5

        return {"reply": reply_text, "confidence": confidence_score}
