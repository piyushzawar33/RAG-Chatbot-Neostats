# import streamlit as st
# from tavily import TavilyClient

# # Local imports
# from utils.rag import ensure_index_ready, retrieve
# from models.llm import generate_answer
# from config.config import WEB_SEARCH_API_KEY


# st.set_page_config(page_title="Podcast Q&A Assistant", layout="wide")

# tavily = TavilyClient(api_key=WEB_SEARCH_API_KEY) if WEB_SEARCH_API_KEY else None

# ensure_index_ready()

# with st.sidebar:
#     st.title("Settings")
    
#     mode = st.radio("Response Style:", ["Concise", "Detailed"])
#     use_web = st.checkbox("Use Web Search Fallback", value=False)


# # MAIN UI
# st.title("Podcast Question Answering Assistant")
# st.write("Ask questions related to the **Elon Musk and Nikhil Kamath's** recent Tech podcast.")

# query = st.text_input("Enter your question:")
# MAX_CONTEXT_CHARS = 2000
# final_context = final_context[:MAX_CONTEXT_CHARS]

# if st.button("Generate Answer") and query.strip():
#     with st.spinner("Retrieving relevant transcript context..."):
#         chunks, score = retrieve(query)   # Top-3
#         chunks = sorted(chunks, key=lambda c: c["start"])
#         context_text = "\n\n".join([c["text"] for c in chunks])
#         relevant = score >= 0.45
#         need_fallback = use_web and (not relevant)

# # Web Search Fallback
#     web_context = ""
#     if need_fallback and tavily:
#         with st.spinner("Using web search fallback..."):
#             try:
#                 resp = tavily.search(query)
#                 web_context = resp.get("answer", "")

#                 if not web_context:
#                     results = resp.get("results", [])
#                     if results:
#                         web_context = results[0].get("content", "")

#             except Exception as e:
#                 st.error(f"Web search failed: {e}")
#                 web_context = ""


#     final_context = context_text
#     if web_context:
#         final_context += "\n\nWeb Search Result:\n" + web_context

#     # LLM Answer
#     with st.spinner("Generating answer..."):
#         answer = generate_answer(mode, query, final_context)


#     st.subheader("Answer:")
#     st.write(answer)

#     st.markdown("---")

#     if web_context:
#         with st.expander("Web Search Result"):
#             st.write(web_context)




import streamlit as st

from utils.rag import ensure_index_ready, retrieve
from models.llm import generate_answer
from config.config import WEB_SEARCH_API_KEY
from tavily import TavilyClient


st.set_page_config(page_title="Podcast Q&A Assistant", layout="wide")

# Tavily client (only if key is available)
tavily = TavilyClient(api_key=WEB_SEARCH_API_KEY) if WEB_SEARCH_API_KEY else None

# Load FAISS index (Fast — no embedding on cloud)
ensure_index_ready()


with st.sidebar:
    st.title("Settings")

    mode = st.radio("Response Style", ["Concise", "Detailed"])
    use_web = st.checkbox("Use Web Search Fallback", value=False)

    st.markdown("---")
    st.markdown("Podcast Q&A System using Gemini + FAISS RAG")
    st.caption("NeoStats AI Engineer Case Study")


st.title("Podcast Question Answering Assistant")
st.write("Ask questions related to the Elon Musk × Nikhil Kamath podcast.")

query = st.text_input("Enter your question:")

if st.button("Generate Answer") and query.strip():

    with st.spinner("Retrieving relevant transcript context..."):
        chunks, score = retrieve(query, top_k=3)

        # Sort chunks by transcript order
        chunks = sorted(chunks, key=lambda c: c["start"])

        # Merge retrieved chunk text
        context_text = "\n\n".join([c["text"] for c in chunks])

        # Semantic similarity check
        relevant = score >= 0.40

        need_fallback = use_web and not relevant


    web_context = ""
    if need_fallback and tavily:
        with st.spinner("Using web search fallback..."):
            try:
                resp = tavily.search(query)
                web_context = resp.get("answer", "")

                # If no direct answer, use first result snippet
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

    # Streamlit Cloud safe limit
    MAX_CONTEXT_CHARS = 2000
    final_context = final_context[:MAX_CONTEXT_CHARS]

    with st.spinner("Generating answer using Gemini..."):
        answer = generate_answer(mode, query, final_context)


    st.subheader("Answer")
    st.write(answer)

    st.markdown("---")

    # Debug context viewer
    with st.expander("Transcript Context (RAG Debug Info)"):
        st.write(context_text)

    if web_context:
        with st.expander("Web Search Context (Debug Info)"):
            st.write(web_context)
