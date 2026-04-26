🔬 Agentic AI Research Assistant
An intelligent, agentic research assistant powered by Retrieval-Augmented Generation (RAG) and large language models. It combines a Python backend with a JavaScript frontend to deliver context-aware, document-grounded answers to complex research queries.

📌 Table of Contents

Overview
Architecture
Tech Stack
Project Structure
Getting Started

Prerequisites
Environment Setup
Running Locally
Running with Docker


Testing
Deployment
Contributing


Overview
The Agentic AI Research Assistant is a full-stack AI application designed to answer research questions by retrieving relevant context from a document corpus and generating accurate, grounded responses via an LLM. Rather than relying solely on the model's parametric knowledge, it uses a RAG pipeline to fetch and inject real document context — making responses more reliable and verifiable.
Key capabilities:

Agentic query processing with context-aware retrieval
RAG pipeline for document-grounded LLM responses
Modular LLM integration (swappable model backend)
Clean web UI for interactive research sessions
Docker-ready for easy deployment


Architecture
User Query
    │
    ▼
[ Frontend / UI ]
    │  HTTP
    ▼
[ Backend API ]
    │
    ├──► [ RAG Module ]
    │         │
    │         ├── Document ingestion & chunking
    │         ├── Embedding & vector storage
    │         └── Semantic retrieval
    │
    └──► [ LLM Module ]
              │
              ├── Context injection
              └── Response generation
The system follows a clean separation of concerns:

rag/ handles document ingestion, embedding, and retrieval
llm/ handles model interaction and prompt construction
backend/ exposes a REST API connecting both modules
frontend/ & ui/ provide the interactive web interface
data/ stores the document corpus used for retrieval


Tech Stack
LayerTechnologyLanguagePython, JavaScriptLLM IntegrationConfigurable via .env (Ollama / API-based)RAGCustom pipeline (embedding + vector retrieval)BackendPython (FastAPI / Flask)FrontendVanilla JS + CSSContainerizationDockerProcess ManagementProcfile (Heroku-compatible)

Project Structure
agentic-ai-research-assistant/
├── backend/            # API server — connects RAG and LLM modules
├── data/               # Document corpus for RAG ingestion
├── frontend/           # Web interface (HTML/CSS/JS)
├── llm/                # LLM client and prompt logic
├── rag/                # Embedding, indexing, and retrieval pipeline
├── ui/                 # Additional UI assets or components
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container build instructions
├── .dockerignore       # Docker build exclusions
├── Procfile            # Process declarations for deployment
├── .env.example        # Environment variable template
├── DEPLOYMENT.md       # Deployment guide
├── test_env.py         # Environment/config validation tests
├── test_llm.py         # LLM module unit tests
├── test_rag.py         # RAG pipeline unit tests
└── test_full_rag.py    # End-to-end RAG integration tests

Getting Started
Prerequisites

Python 3.9+
Node.js (for frontend tooling, if applicable)
Docker (optional, for containerized setup)
An LLM backend — local (e.g., Ollama) or API-based

Environment Setup

Clone the repository:

bashgit clone https://github.com/Sparsh075/agentic-ai-research-assistant.git
cd agentic-ai-research-assistant

Create and activate a virtual environment:

bashpython -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

Install dependencies:

bashpip install -r requirements.txt

Configure environment variables:

bashcp .env.example .env
# Edit .env with your LLM API keys or local model settings
Running Locally
bashpython main.py
Then open your browser and navigate to the URL shown in the terminal (typically http://localhost:8000).
Running with Docker
bash# Build the image
docker build -t agentic-ai-research-assistant .

# Run the container
docker run -p 8000:8000 --env-file .env agentic-ai-research-assistant

Testing
The project includes a layered test suite covering environment config, individual modules, and full pipeline integration.
bash# Verify environment and configuration
python test_env.py

# Test LLM module in isolation
python test_llm.py

# Test RAG retrieval pipeline
python test_rag.py

# Run full end-to-end RAG test
python test_full_rag.py
Run all tests at once:
bashpython -m pytest test_*.py -v

Deployment
See DEPLOYMENT.md for full deployment instructions.
The project includes a Procfile for Heroku-compatible platforms and a Dockerfile for container-based cloud deployments (Railway, Render, AWS, GCP, etc.).

Contributing
Contributions, issues, and feature requests are welcome. Feel free to open a PR or issue.

Fork the repo
Create a feature branch: git checkout -b feature/your-feature
Commit your changes: git commit -m 'Add your feature'
Push to the branch: git push origin feature/your-feature
Open a Pull Request
