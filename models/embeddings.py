import numpy as np
import google.generativeai as genai
from config.config import GEMINI_API_KEY, GEMINI_EMBED_MODEL

genai.configure(api_key=GEMINI_API_KEY)


def embed_texts(texts):
    response = genai.embed_content(model=GEMINI_EMBED_MODEL, content=texts)

    if isinstance(response, list):
        return np.array(response, dtype="float32")

    if isinstance(response, dict) and "embedding" in response:
        return np.array(response["embedding"], dtype="float32")

    if hasattr(response, "embedding"):
        return np.array(response.embedding, dtype="float32")

    raise ValueError("Unknown embedding response format:", response)
