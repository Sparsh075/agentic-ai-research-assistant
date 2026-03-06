from sentence_transformers import SentenceTransformer

# Lightweight, fast, high-quality embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list):
    return model.encode(texts, show_progress_bar=True)
