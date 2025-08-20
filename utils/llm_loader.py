# utils/llm_loader.py
import os
import time
import httpx
from langchain_groq import ChatGroq

def load_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("❌ GROQ_API_KEY not set in environment")

    # Disable SSL verification (⚠️ only for local testing)
    insecure_client = httpx.Client(verify=False)

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",  # or your preferred Groq model
        temperature=0.2,
        max_tokens=1000,
        http_client=insecure_client,   # 👈 ensure we use same insecure client
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
