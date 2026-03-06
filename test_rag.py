from rag.pdf_loader import load_and_chunk_pdf
from rag.embeddings import embed_texts
from rag.vector_store import build_faiss_index
from rag.retriever import retrieve_top_k

# Load PDF chunks
chunks = load_and_chunk_pdf("data/transformer_paper.pdf")

# Embed chunks
embeddings = embed_texts(chunks)

# Build FAISS index
index = build_faiss_index(embeddings)

# Query
query = "What is self-attention in Transformer?"
results = retrieve_top_k(query, chunks, index, k=3)

print("\n🔍 Query Results:\n")
for i, res in enumerate(results, 1):
    print(f"Result {i}:\n{res[:500]}\n")
