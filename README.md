# 🔬 Agentic AI Research Assistant  
### Intelligent RAG-Based Research System with LLM Integration

---

## 📌 Overview

The **Agentic AI Research Assistant** is a full-stack AI system designed to answer complex research queries using **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)**.

Instead of relying only on pre-trained knowledge, the system:
- Retrieves relevant context from a document corpus  
- Injects it into the LLM  
- Generates **accurate, grounded, and explainable responses**  

This results in **more reliable and context-aware outputs**.

---

## 🚀 Key Features

- 🤖 **LLM-Powered Responses**  
  Generates intelligent answers using configurable LLM backends (Ollama / API)

- 🔎 **RAG Pipeline**  
  Retrieves relevant documents and injects context into responses

- 🧠 **Agentic Query Processing**  
  Multi-step pipeline for reasoning, retrieval, and response generation

- 🔄 **Modular Architecture**  
  Easily switch models, embeddings, or retrieval strategies

- 🌐 **Interactive Web UI**  
  Clean interface for research queries

- 🐳 **Docker Support**  
  Fully containerized for easy deployment

---

## 🏗️ System Architecture


User Query
│
▼
[ Frontend / UI ]
│ HTTP
▼
[ Backend API ]
│
├──► [ RAG Module ]
│ │
│ ├── Document ingestion & chunking
│ ├── Embedding & vector storage
│ └── Semantic retrieval
│
└──► [ LLM Module ]
│
├── Context injection
└── Response generation


---

## ⚙️ Architecture Breakdown

- **rag/** → Handles document ingestion, embeddings, and retrieval  
- **llm/** → Handles model interaction and prompt construction  
- **backend/** → REST API connecting all modules  
- **frontend/** → Web interface for user interaction  
- **data/** → Document corpus for retrieval  

---

## 🧠 Data Structures & Algorithms (DSA)

This project integrates core DSA concepts:

- **Graph (Knowledge Mapping)** → Topic relationships  
- **BFS / DFS** → Traversing related concepts  
- **Priority Queue (Heap)** → Ranking results  
- **Hash Maps** → Fast lookup and caching  

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Language | Python, JavaScript |
| Backend | FastAPI / Flask |
| Frontend | HTML, CSS, JavaScript |
| LLM | Ollama / API-based |
| RAG | Custom embedding + retrieval pipeline |
| Containerization | Docker |
| Deployment | Procfile (Heroku compatible) |

---

## 📂 Project Structure

agentic-ai-research-assistant/
│
├── backend/ # API server (connects RAG + LLM)
├── data/ # Document corpus
├── frontend/ # Web interface
├── llm/ # LLM logic
├── rag/ # Retrieval pipeline
├── ui/ # UI components/assets
│
├── main.py # Entry point
├── requirements.txt # Dependencies
├── Dockerfile # Container setup
├── Procfile # Deployment config
├── .env.example # Environment template
├── DEPLOYMENT.md # Deployment guide
│
├── test_env.py # Environment tests
├── test_llm.py # LLM tests
├── test_rag.py # RAG tests
└── test_full_rag.py # Integration tests


---

## ⚡ Getting Started

### 🔹 Prerequisites

- Python 3.9+  
- Node.js (optional)  
- Docker (optional)  
- LLM backend (Ollama or API key)

---

### 🔹 Installation

```bash
git clone https://github.com/Sparsh075/agentic-ai-research-assistant.git
cd agentic-ai-research-assistant

🔹 Setup Virtual Environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
🔹 Install Dependencies
pip install -r requirements.txt
🔹 Configure Environment
cp .env.example .env

Edit .env with:

API keys OR
local model configuration
▶️ Running the Project
Run Locally
python main.py

Open:

http://localhost:8000
🐳 Run with Docker
docker build -t agentic-ai-research-assistant .
docker run -p 8000:8000 --env-file .env agentic-ai-research-assistant
🧪 Testing

Run individual modules:

python test_env.py
python test_llm.py
python test_rag.py
python test_full_rag.py

Run all tests:

python -m pytest test_*.py -v
🚀 Deployment

Refer to DEPLOYMENT.md for full instructions.

Supports:

Heroku (Procfile)
Docker-based platforms (Railway, Render, AWS, GCP)
🤝 Contributing

Contributions are welcome!

git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature

Then open a Pull Request.

👨‍💻 Author

Sparsh Modi
GitHub: https://github.com/Sparsh075
