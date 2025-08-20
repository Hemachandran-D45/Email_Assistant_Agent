import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Set it with: setx GROQ_API_KEY 'your_key_here'")

# Disable SSL verification (test only!)
import httpx
insecure_client = httpx.Client(verify=False)

llm = ChatGroq(
    api_key=api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    max_tokens=200,
    http_client=insecure_client,  # 👈 force no SSL verify
)

response = llm.invoke("Hello Groq! Can you confirm this test is working?")
print("✅ Response:", response)
