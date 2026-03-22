import os

from google import genai


def build_context_prompt(user_question: str, context_dict: dict) -> str:
    """Create a grounded prompt for the RESQnet AI assistant."""
    context_lines = "\n".join(f"- {key}: {value}" for key, value in context_dict.items())
    return (
        "You are RESQnet, a disaster response system.\n"
        "You explain risk levels, map zones (red high, yellow medium, green low), safe zones, and recommended actions.\n"
        "Always answer based on the provided data only.\n"
        "Be practical, concise, and action-oriented.\n\n"
        f"Current context:\n{context_lines}\n\n"
        f"User question: {user_question}"
    )


def build_fallback_response(context_dict: dict) -> str:
    """Provide a grounded fallback message if Gemini is unavailable."""
    return (
        f"{context_dict['Disaster Type']} conditions in {context_dict['Region']} are currently "
        f"{str(context_dict['Risk Level']).lower()} risk with a score of {context_dict['Risk Score']}. "
        f"Estimated affected population is {context_dict['Affected Population']}. "
        f"Safe zone guidance points people toward {context_dict['Safe Zone']}. "
        f"Recommended action: {context_dict['Warning Message']}"
    )


def get_gemini_response(user_question: str, context_dict: dict) -> str:
    """Return a Gemini response grounded in the current dashboard context."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your environment variables before using the AI assistant."
        )

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=build_context_prompt(user_question, context_dict),
        )

        if not getattr(response, "text", None):
            return build_fallback_response(context_dict)
    except Exception:
        return build_fallback_response(context_dict)

    return response.text.strip()
