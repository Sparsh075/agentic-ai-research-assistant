from time import perf_counter
from typing import Iterable, Optional

from backend.app_logger.logger import get_logger
from backend.llm.llm_router import generate_response
from backend.rag.pdf_loader import load_and_chunk_pdf_with_metadata


class RAGPipeline:
    _embedder = None
    _faiss = None
    _np = None

    def __init__(self, pdf_path: Optional[str] = None):
        self.logger = get_logger("rag-pipeline")
        self.embedder = self._get_embedder()
        self.index = None
        self.text_chunks = []
        self.chunk_records = []
        self.document_name = None
        self.documents = []
        self.chat_history = []

        if pdf_path:
            self.load_pdf(pdf_path)

    @classmethod
    def _get_embedder(cls):
        if cls._embedder is None:
            from sentence_transformers import SentenceTransformer

            cls._embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return cls._embedder

    @classmethod
    def _get_faiss(cls):
        if cls._faiss is None:
            import faiss

            cls._faiss = faiss
        return cls._faiss

    @classmethod
    def _get_numpy(cls):
        if cls._np is None:
            import numpy as np

            cls._np = np
        return cls._np

    def build_index(self, records: Iterable[dict]):
        faiss = self._get_faiss()
        np = self._get_numpy()
        self.chunk_records = list(records)
        self.text_chunks = [record["text"] for record in self.chunk_records]
        emb_start = perf_counter()
        embeddings = self.embedder.encode(self.text_chunks)
        emb_ms = (perf_counter() - emb_start) * 1000
        self.logger.info(f"Embedding generation: {emb_ms:.1f}ms")
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

    def load_pdf(self, pdf_path: str):
        self.chunk_records = []
        self.text_chunks = []
        self.index = None
        self.documents = []
        self.add_pdf(pdf_path)

    def add_pdf(self, pdf_path: str):
        records = load_and_chunk_pdf_with_metadata(pdf_path)
        if not records:
            raise ValueError("No text extracted from PDF.")
        self.document_name = pdf_path.replace("\\", "/").split("/")[-1]
        if self.document_name not in self.documents:
            self.documents.append(self.document_name)
        enriched = []
        existing_count = len(self.chunk_records)
        for record in records:
            enriched.append(
                {
                    "text": record["text"],
                    "page_number": record["page_number"],
                    "chunk_id": f"{self.document_name}_{existing_count}_{record['chunk_id']}",
                    "document": self.document_name,
                }
            )
        all_records = self.chunk_records + enriched
        self.build_index(all_records)

    def retrieve_with_sources(self, query: str, k: int = 3) -> list[dict]:
        if self.index is None:
            return []
        np = self._get_numpy()
        t0 = perf_counter()
        query_vec = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_vec), k)
        sources = []

        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.chunk_records):
                continue
            distance = float(distances[0][rank])
            score = 1.0 / (1.0 + distance)
            record = self.chunk_records[idx]
            snippet = record["text"][:280].strip()
            sources.append(
                {
                    "page_number": record["page_number"],
                    "snippet": snippet,
                    "score": round(score, 4),
                    "document": record.get("document", self.document_name or "Uploaded PDF"),
                    "chunk_id": record.get("chunk_id", str(idx)),
                }
            )
        retrieval_ms = (perf_counter() - t0) * 1000
        self.logger.info(f"RAG retrieval: {retrieval_ms:.1f}ms")
        return sources

    def _context_from_sources(self, sources: list[dict]) -> str:
        context_chunks = []
        for source in sources:
            chunk_id = source.get("chunk_id")
            matching = next(
                (record for record in self.chunk_records if record.get("chunk_id") == chunk_id),
                None,
            )
            if matching:
                context_chunks.append(matching["text"])
        return "\n".join(context_chunks)

    def _format_history(self, history: Optional[list[dict]]) -> str:
        if history is None:
            return "\n".join(self.chat_history[-8:])

        lines = []
        for msg in history[-8:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            label = "User" if role == "user" else "Assistant"
            lines.append(f"{label}: {content}")
        return "\n".join(lines)

    def build_prompt(
        self,
        question: str,
        history: Optional[list[dict]] = None,
        sources: Optional[list[dict]] = None,
    ) -> str:
        if self.index is None:
            raise ValueError("RAG pipeline not initialized. Load PDF first.")

        selected_sources = sources if sources is not None else self.retrieve_with_sources(question)
        context = self._context_from_sources(selected_sources)
        history_text = self._format_history(history)

        return f"""You are a research assistant. Answer concisely based on the context.

{history_text}

Context:
{context}

Question: {question}

Answer:"""

    def ask(
        self,
        question: str,
        history: Optional[list[dict]] = None,
        model: Optional[str] = None,
        fast: bool = False,
        settings: Optional[dict] = None,
    ) -> str:
        response = self.ask_with_sources(
            question=question,
            history=history,
            model=model,
            fast=fast,
            settings=settings,
        )
        return response["answer"]

    def ask_with_sources(
        self,
        question: str,
        history: Optional[list[dict]] = None,
        model: Optional[str] = None,
        fast: bool = False,
        settings: Optional[dict] = None,
    ) -> dict:
        if self.index is None:
            return {
                "answer": "RAG pipeline not initialized. Load PDF first.",
                "sources": [],
            }

        use_rag = True
        top_k = 3
        if settings:
            use_rag = bool(settings.get("rag_enabled", True))
            maybe_top_k = settings.get("top_k")
            if isinstance(maybe_top_k, int):
                top_k = max(1, min(10, maybe_top_k))

        sources = self.retrieve_with_sources(question, k=top_k) if use_rag else []
        prompt = self.build_prompt(question, history, sources=sources)
        response_text = generate_response(
            prompt,
            model=model,
            fast=fast,
            options=settings.get("ollama_options") if settings else None,
        )

        if history is None:
            self.chat_history.append(f"User: {question}")
            self.chat_history.append(f"Assistant: {response_text}")

        return {
            "answer": response_text,
            "sources": sources,
        }

    def query(self, question: str):
        return self.ask(question)

    def answer(self, question: str):
        return self.ask(question)
