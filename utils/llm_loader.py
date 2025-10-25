# utils/llm_loader.py
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

def load_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in environment")

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",  # updated stable Groq model
        temperature=0.2,
        max_tokens=1000,
    )

    # wrap with retry
    class SafeLLM:
        def __init__(self, llm):
            self.llm = llm

        def invoke(self, prompt, retries=3, delay=2):
            for attempt in range(retries):
                try:
                    return self.llm.invoke(prompt)
                except Exception as e:
                    if attempt < retries - 1:
                        print(f"⚠️ Groq call failed: {e}, retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        raise

    return SafeLLM(llm)
