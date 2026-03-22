import os

from google import genai


def build_context_prompt(user_question: str, context_dict: dict) -> str:
    """Create a grounded prompt for the RESQnet AI assistant."""
    context_lines = "\n".join(f"- {key}: {value}" for key, value in context_dict.items())
    return (
        "You are RESQnet AI Assistant, a concise disaster response assistant.\n"
        "Use only the current dashboard context below.\n"
        "Be practical, clear, and action-oriented.\n"
        "If the risk is high, emphasize urgent action.\n"
        "If the risk is medium, emphasize preparedness.\n"
        "If the risk is low, emphasize monitoring.\n\n"
        f"Current context:\n{context_lines}\n\n"
        f"User question: {user_question}"
    )


def get_gemini_response(user_question: str, context_dict: dict) -> str:
    """Return a Gemini response grounded in the current dashboard context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your environment variables before using the AI assistant."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=build_context_prompt(user_question, context_dict),
    )

    if not getattr(response, "text", None):
        raise ValueError("The AI assistant returned an empty response. Please try again.")

    return response.text.strip()
