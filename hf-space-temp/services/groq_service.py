"""
Groq API wrapper for LLM inference.
Uses LangChain's ChatGroq for structured interactions with Llama 3.
"""
from langchain_groq import ChatGroq
from backend.app.config import get_settings

settings = get_settings()

def get_llm():
    """Initializes and returns the ChatGroq LLM instance."""
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        # Using Llama 3.3 (70B) - it's free, incredibly fast on Groq, and smart.
        model_name="llama-3.3-70b-versatile", 
        temperature=0.1 # Low temperature for factual, deterministic RCA
    )

def query_llm(prompt: str) -> str:
    """Sends a prompt to the LLM and returns the text response."""
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content