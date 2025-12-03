import streamlit as st
from tavily import TavilyClient

# Local imports
from utils.rag import ensure_index_ready, retrieve
from models.llm import generate_answer
from config.config import WEB_SEARCH_API_KEY


st.set_page_config(page_title="Podcast Q&A Assistant", layout="wide")

tavily = TavilyClient(api_key=WEB_SEARCH_API_KEY) if WEB_SEARCH_API_KEY else None

ensure_index_ready()

with st.sidebar:
    st.title("Settings")
    
    mode = st.radio("Response Style:", ["Concise", "Detailed"])
    use_web = st.checkbox("Use Web Search Fallback", value=False)


# MAIN UI
st.title("Podcast Question Answering Assistant")
st.write("Ask questions related to the **Elon Musk and Nikhil Kamath's** recent Tech podcast.")

query = st.text_input("Enter your question:")
MAX_CONTEXT_CHARS = 2000
final_context = final_context[:MAX_CONTEXT_CHARS]

if st.button("Generate Answer") and query.strip():
    with st.spinner("Retrieving relevant transcript context..."):
        chunks, score = retrieve(query)   # Top-3
        chunks = sorted(chunks, key=lambda c: c["start"])
        context_text = "\n\n".join([c["text"] for c in chunks])
        relevant = score >= 0.45
        need_fallback = use_web and (not relevant)

# Web Search Fallback
    web_context = ""
    if need_fallback and tavily:
        with st.spinner("Using web search fallback..."):
            try:
                resp = tavily.search(query)
                web_context = resp.get("answer", "")

                if not web_context:
                    results = resp.get("results", [])
                    if results:
                        web_context = results[0].get("content", "")

            except Exception as e:
                st.error(f"Web search failed: {e}")
                web_context = ""


    final_context = context_text
    if web_context:
        final_context += "\n\nWeb Search Result:\n" + web_context

    # LLM Answer
    with st.spinner("Generating answer..."):
        answer = generate_answer(mode, query, final_context)


    st.subheader("Answer:")
    st.write(answer)

    st.markdown("---")

    if web_context:
        with st.expander("Web Search Result"):
            st.write(web_context)

