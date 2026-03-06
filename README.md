# Agentic AI Research Assistant

An intelligent AI-powered research assistant that allows users to upload research papers (PDFs) and interact with them through natural language queries. The system uses Retrieval-Augmented Generation (RAG) to extract knowledge from documents and answer questions with contextual understanding.

This project combines modern AI technologies including large language models, vector search, and a modern web interface to create a powerful knowledge exploration tool.

---

## Features

* Upload research papers (PDF)
* Automatic document indexing
* Retrieval-Augmented Generation (RAG)
* Semantic search using embeddings
* Streaming AI responses
* Multi-model LLM routing
* Groq-powered high-speed inference
* Session-based chat memory
* Modern React chat interface

---

## Tech Stack

### Backend

* Python
* FastAPI
* FAISS Vector Database
* Sentence Transformers
* Groq API
* Ollama (local LLM fallback)

### Frontend

* React
* Vite
* TailwindCSS
* Streaming Chat UI

### AI / ML

* Llama 3 Models
* RAG Pipeline
* Embedding Models (MiniLM)

---

## Project Architecture

The system follows a Retrieval-Augmented Generation architecture.

User queries are first used to retrieve relevant document chunks from a vector database. These chunks are then provided as context to a large language model which generates the final response.

```
User
 │
 ▼
React Frontend (Chat UI)
 │
 ▼
FastAPI Backend
 │
 ├── Session Manager
 │
 ├── RAG Pipeline
 │      │
 │      ├── PDF Loader
 │      ├── Text Chunking
 │      ├── Embedding Generator
 │      └── FAISS Vector Search
 │
 ▼
LLM Router
 │
 ├── Groq (Primary Inference)
 └── Ollama (Local Fallback)
 │
 ▼
Generated Answer
 │
 ▼
Streaming Response to UI
```

---

## How the System Works

1. A user uploads a research paper (PDF).
2. The backend extracts text and splits it into smaller chunks.
3. Each chunk is converted into a vector embedding.
4. Embeddings are stored in a FAISS vector database.
5. When a question is asked:

   * The question is converted into an embedding.
   * Similar document chunks are retrieved.
   * These chunks are sent to the LLM as context.
6. The LLM generates a contextual answer.

---

## Installation

Clone the repository:

```
git clone https://github.com/Sparsh075/agentic-ai-research-assistant.git
cd agentic-ai-research-assistant
```

### Backend Setup

```
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 9000
```

### Frontend Setup

```
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Create a `.env` file using `.env.example`.

Example:

```
LLM_PROVIDER=groq
GROQ_API_KEY=your_api_key_here
PORT=9000
```

---

## Example Use Cases

* Research paper analysis
* Academic literature exploration
* Knowledge extraction from documents
* AI-powered study assistant
* Technical document Q&A

---

## Future Improvements

* Multi-document knowledge base
* Persistent vector database
* Authentication system
* Cloud deployment
* Advanced agent workflows
* Multi-modal document support

---

## License

MIT License

---

## Author

Sparsh
Computer Science Student | AI & Machine Learning Enthusiast
