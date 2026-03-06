from rag.rag_pipeline import RAGPipeline

rag = RAGPipeline("data/transformer_paper.pdf")

query = "Explain multi-head self-attention in Transformer."

answer = rag.answer(query)

print("\n🧠 RAG Answer:\n")
print(answer)
