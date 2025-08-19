import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env
load_dotenv()

def load_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").lower()  # default to Groq
    
    if provider == "groq":
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2
        )
    
    # elif provider == "gemini":
    #     return ChatGoogleGenerativeAI(
    #         model=os.getenv("GEMINI_MODEL", "gemini-pro"),
    #         google_api_key=os.getenv("GEMINI_API_KEY"),
    #         temperature=0.2
    #     )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
