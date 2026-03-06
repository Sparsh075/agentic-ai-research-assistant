# Deployment Notes

## Local setup

1. Create and activate virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy `.env.example` to `.env` and fill values.
4. Start backend:
   uvicorn backend.main:app --host 0.0.0.0 --port 9000 --reload

## Production setup

Set environment variables:
- `LLM_PROVIDER=groq`
- `GROQ_API_KEY=<secret>`
- `ENVIRONMENT=production`
- `DEBUG=false`
- `PORT=<platform_port>`
- `CORS_ORIGINS=https://your-frontend-domain`

Start command:
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}

Health endpoint:
- `GET /healthz`

Provider diagnostics:
- `GET /llm-config`
