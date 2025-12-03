import os
import json
import numpy as np
import faiss

from models.embeddings import embed_texts
from utils.transcript_loader import load_cleaned_transcript


INDEX_PATH = "vector_store/faiss.index"
CHUNKS_PATH = "vector_store/chunks.json"

os.makedirs("vector_store", exist_ok=True)

faiss_index = None
chunks_data = None
_index_built = False


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    n = len(words)
    chunks = []

    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append({"text": " ".join(words[start:end]), "start": start, "end": end})

        next_start = end - overlap
        start = end if next_start <= start else next_start

    return chunks


def build_index_from_chunks(chunks):
    global faiss_index, chunks_data

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts).astype("float32")

    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(embeddings)

    faiss.write_index(faiss_index, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

    chunks_data = chunks
    print("FAISS index built.")


def load_index():
    global faiss_index, chunks_data

    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        return False

    try:
        faiss_index = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
        return True
    except:
        return False


def ensure_index_ready():
    global _index_built, faiss_index, chunks_data

    if _index_built:
        return

    if load_index():
        _index_built = True
        return

    text = load_cleaned_transcript()
    chunks = chunk_text(text)
    build_index_from_chunks(chunks)
    _index_built = True


def retrieve(query, top_k=3):
    if faiss_index is None or chunks_data is None:
        ensure_index_ready()

    q_vec = embed_texts([query]).astype("float32")
    distances, indices = faiss_index.search(q_vec, top_k)

    retrieved = []
    for idx in indices[0]:
        if idx >= 0:
            retrieved.append(chunks_data[int(idx)])

    best_dist = float(distances[0][0])
    confidence = 1 / (1 + best_dist)

    return retrieved, confidence
