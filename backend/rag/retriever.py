import numpy as np
from .embeddings import embed_texts

def retrieve_top_k(query, chunks, index, k=3):
    query_embedding = embed_texts([query])
    distances, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0]]
