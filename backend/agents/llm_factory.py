from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from config import settings

def get_llm():
    """Instantiate the appropriate LLM based on configured API keys."""
    if settings.gemini_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=settings.gemini_api_key,
            temperature=0.2
        )
    elif settings.groq_api_key:
        return ChatGroq(
            model="llama3-70b-8192",
            api_key=settings.groq_api_key,
            temperature=0.2
        )
    else:
        # Fallback to OpenAI if still somehow using it
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2
        )
