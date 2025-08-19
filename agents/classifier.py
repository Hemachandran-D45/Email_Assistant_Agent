from langchain.prompts import PromptTemplate
from utils.llm_loader import llm

class ClassifierAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["email_body"],
            template="""
Classify the following email into a category and tone:

Email:
{email_body}

Return JSON with keys: category, tone
            """
        )

    def classify(self, email_body: str):
        response = llm.predict(self.prompt.format(email_body=email_body))

        import json
        try:
            parsed = json.loads(response)
        except:
            parsed = {"category": "unknown", "tone": "neutral"}

        return parsed
