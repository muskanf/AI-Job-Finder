# retriever.py  ─────────────────────────────────────────────────────
"""
Thin ChromaDB wrapper: stores captions => similarity score (0-1)
"""
from __future__ import annotations
import chromadb, hashlib, pathlib, numpy as np
import chromadb.utils.embedding_functions as ef
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHROMA_DIR = pathlib.Path(".chroma_viralvisor")
COLL_NAME  = "captions"

openai_ef = ef.OpenAIEmbeddingFunction(
    api_key=ai.api_key,
    model_name="text-embedding-3-small",
    dimensions=256,
)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
try:
    coll = client.get_collection(COLL_NAME, embedding_function=openai_ef)
except chromadb.errors.NotFoundError:
    coll = client.create_collection(COLL_NAME, embedding_function=openai_ef)

# ----------  public helpers  --------------------------------------
def add_caption(text: str):
    """Add caption text to vector DB (id = md5 hash)."""
    cid = hashlib.md5(text.encode()).hexdigest()
    try:
        coll.add(ids=[cid], documents=[text])
    except chromadb.errors.IDAlreadyExistsError:
        pass

def similarity(text: str, k: int = 5) -> float:
    """Return similarity 0-1 (higher = more similar)."""
    if coll.count() == 0:
        return 0.0
    res = coll.query(query_texts=[text], n_results=min(k, coll.count()))
    dists = res["distances"][0]
    return round(1 / (1 + np.mean(dists)), 3)

