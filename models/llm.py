import google.generativeai as genai
from config.config import GEMINI_API_KEY, GEMINI_CHAT_MODEL

genai.configure(api_key=GEMINI_API_KEY)


def generate_answer(mode, query, context):
    style = (
        "Respond concisely in 3–5 lines."
        if mode == "Concise"
        else "Provide a detailed well-structured explanation."
    )

    prompt = f"""
You are a helpful assistant answering questions based on a podcast.
Use the provided transcript context when possible.
If the context is insufficient, rely on fallback or say so.

                User question:
                {query}

                Retrieved context:
                {context}

                {style}
    """

    try:
        model = genai.GenerativeModel(model_name=GEMINI_CHAT_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Sorry, I ran into an error while generating the answer."
