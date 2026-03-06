from __future__ import annotations

import json
import traceback
from time import perf_counter
from urllib.parse import quote

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.config import get_settings
from backend.logging.logger import get_logger
from backend.models.schemas import (
    AskRequest,
    LegacyAskRequest,
    ProjectCreateRequest,
    SessionCreateRequest,
    SessionSettings,
)
from backend.project_manager import ProjectManager
from llm.llm_router import build_ollama_options, get_llm_config, stream_response


logger = get_logger("api")
settings = get_settings()
app = FastAPI(title="Agentic AI Research Assistant", debug=settings.debug)
project_manager = ProjectManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info(
        f"startup environment={settings.environment} debug={settings.debug} "
        f"provider={settings.llm_provider} host={settings.host} port={settings.port}"
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = perf_counter()
    try:
        response = await call_next(request)
        elapsed = perf_counter() - start
        logger.info(
            f"{request.url.path} request completed in {elapsed:.2f}s (status={response.status_code})"
        )
        return response
    except Exception as exc:
        elapsed = perf_counter() - start
        logger.error(f"{request.url.path} failed in {elapsed:.2f}s: {exc}\n{traceback.format_exc()}")
        raise


def _sanitize_settings(settings: SessionSettings) -> SessionSettings:
    settings.temperature = max(0.0, min(1.0, float(settings.temperature)))
    settings.max_tokens = max(32, min(2048, int(settings.max_tokens)))
    settings.top_k = max(1, min(10, int(settings.top_k)))
    settings.fast_mode = bool(settings.fast_mode)
    settings.rag_enabled = bool(settings.rag_enabled)
    return settings


def _settings_to_runtime(settings: SessionSettings) -> dict:
    return {
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "rag_enabled": settings.rag_enabled,
        "top_k": settings.top_k,
        "ollama_options": build_ollama_options(
            {"temperature": settings.temperature, "max_tokens": settings.max_tokens},
            fast=settings.fast_mode,
        ),
    }


def _estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def _ensure_default_project_id() -> str:
    projects = project_manager.list_projects()
    if not projects:
        return project_manager.create_project(name="Default Project")["id"]
    return projects[0]["id"]


def _ensure_session_id(project_id: str, session_id: str | None) -> str:
    if session_id:
        return session_id
    sessions = project_manager.list_sessions(project_id)
    if sessions:
        return sessions[0]["id"]
    return project_manager.create_session(project_id, "Default Session", SessionSettings().dict())["id"]


def _resolve_model(question: str, model: str | None, settings: SessionSettings) -> str | None:
    if model:
        return model
    if settings.fast_mode or len(question.strip()) < 40:
        return "tinyllama"
    return "llama3:8b"


def _is_valid_model_name(model: str) -> bool:
    if not model or len(model) > 120:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._:/")
    return all(ch in allowed for ch in model)


def _stream_answer(project_id: str, session_id: str, payload: AskRequest) -> StreamingResponse:
    if payload.model and not _is_valid_model_name(payload.model):
        raise HTTPException(status_code=400, detail="Invalid model name format.")

    try:
        project_manager.get_project(project_id)
        session = project_manager.get_session(project_id, session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    pipeline = project_manager.get_pipeline(project_id)
    if pipeline.index is None:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")

    settings = SessionSettings(**session["settings"])
    if payload.settings is not None:
        settings = _sanitize_settings(payload.settings)
    if payload.fast is not None:
        settings.fast_mode = bool(payload.fast)

    selected_model = _resolve_model(payload.question, payload.model, settings)
    runtime = _settings_to_runtime(settings)
    project_manager.update_session_settings(session_id, settings.dict())

    history = [{"role": m["role"], "content": m["content"]} for m in session["messages"]]
    retrieval_start = perf_counter()
    sources = pipeline.retrieve_with_sources(payload.question, k=runtime["top_k"]) if runtime["rag_enabled"] else []
    retrieval_ms = (perf_counter() - retrieval_start) * 1000
    logger.info(f"RAG retrieval: {retrieval_ms:.1f}ms")

    prompt = pipeline.build_prompt(payload.question, history=history, sources=sources)
    ask_start = perf_counter()

    diagnostics_stub = {
        "model": selected_model or "llama3:8b",
        "response_time": "streaming",
        "tokens_used": 0,
        "retrieval_time": f"{retrieval_ms:.1f}ms",
        "retrieved_chunks": len(sources),
        "top_chunks": [
            {"score": s.get("score", 0), "page": s.get("page_number", 0)}
            for s in sources[:5]
        ],
    }

    def token_stream():
        full_response = ""
        try:
            for token in stream_response(
                prompt=prompt,
                model=selected_model,
                fast=settings.fast_mode,
                options=runtime["ollama_options"],
            ):
                full_response += token
                yield token
        except Exception as exc:
            logger.error(f"Streaming error: {exc}\n{traceback.format_exc()}")
            raise

        response_time = perf_counter() - ask_start
        diagnostics = {
            "model": selected_model or "llama3:8b",
            "response_time": f"{response_time:.2f}s",
            "tokens_used": _estimate_tokens(full_response),
            "retrieval_time": f"{retrieval_ms:.1f}ms",
            "retrieved_chunks": len(sources),
            "top_chunks": [
                {"score": s.get("score", 0), "page": s.get("page_number", 0)}
                for s in sources[:5]
            ],
        }

        project_manager.append_message(session_id, "user", payload.question)
        project_manager.append_message(
            session_id,
            "assistant",
            full_response,
            sources=sources,
            diagnostics=diagnostics,
        )

    headers = {
        "X-Sources": quote(json.dumps(sources)),
        "X-Document": pipeline.document_name or "",
        "X-Diagnostics": quote(json.dumps(diagnostics_stub)),
    }
    return StreamingResponse(token_stream(), media_type="text/plain", headers=headers)


@app.get("/")
def root():
    return {"status": "API is running"}


@app.get("/healthz")
def healthz():
    return {"ok": True, "environment": settings.environment}


@app.get("/llm-config")
def llm_config():
    return get_llm_config()


@app.post("/projects")
def create_project(payload: ProjectCreateRequest):
    project = project_manager.create_project(name=payload.name)
    return {
        "id": project["id"],
        "name": project["name"],
        "created_at": project["created_at"],
        "documents": [],
        "sessions": [],
    }


@app.get("/projects")
def list_projects():
    return project_manager.list_projects()


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    try:
        project = project_manager.get_project(project_id)
        documents = project_manager.list_documents(project_id)
        sessions = project_manager.list_sessions(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": project["id"],
        "name": project["name"],
        "created_at": project["created_at"],
        "documents": [
            {"id": d["id"], "filename": d["filename"], "uploaded_at": d["uploaded_at"]}
            for d in documents
        ],
        "sessions": sessions,
    }


@app.post("/projects/{project_id}/upload-pdf")
async def upload_pdf(project_id: str, file: UploadFile = File(...)):
    try:
        document = project_manager.add_document(project_id, file)
        return {"message": "PDF uploaded and indexed successfully", "document": document}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Upload failed: {exc}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/projects/{project_id}/documents")
def list_documents(project_id: str):
    try:
        return project_manager.list_documents(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/{project_id}/sessions")
def create_session(project_id: str, payload: SessionCreateRequest):
    try:
        session = project_manager.create_session(
            project_id=project_id,
            title=payload.title or "New Session",
            settings=SessionSettings().dict(),
        )
        return {
            "id": session["id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "message_count": 0,
            "settings": session["settings"],
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects/{project_id}/sessions")
def list_sessions(project_id: str):
    try:
        return project_manager.list_sessions(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects/{project_id}/sessions/{session_id}")
def get_session(project_id: str, session_id: str):
    try:
        return project_manager.get_session(project_id, session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/projects/{project_id}/ask/{session_id}")
def ask(project_id: str, session_id: str, payload: AskRequest):
    return _stream_answer(project_id, session_id, payload)


@app.post("/projects/{project_id}/ask-stream/{session_id}")
def ask_stream(project_id: str, session_id: str, payload: AskRequest):
    return _stream_answer(project_id, session_id, payload)


# Legacy aliases
@app.post("/upload-pdf")
async def upload_pdf_legacy(file: UploadFile = File(...)):
    project_id = _ensure_default_project_id()
    return await upload_pdf(project_id, file)


@app.post("/session")
def create_session_legacy(payload: SessionCreateRequest):
    project_id = _ensure_default_project_id()
    return create_session(project_id, payload)


@app.get("/sessions")
def list_sessions_legacy():
    project_id = _ensure_default_project_id()
    return list_sessions(project_id)


@app.get("/session/{session_id}")
def get_session_legacy(session_id: str):
    project_id = _ensure_default_project_id()
    return get_session(project_id, session_id)


@app.post("/ask/{session_id}")
def ask_legacy(session_id: str, payload: AskRequest):
    project_id = _ensure_default_project_id()
    return _stream_answer(project_id, session_id, payload)


@app.post("/ask-stream/{session_id}")
def ask_stream_legacy(session_id: str, payload: AskRequest):
    project_id = _ensure_default_project_id()
    return _stream_answer(project_id, session_id, payload)


@app.post("/ask")
def ask_default_legacy(payload: LegacyAskRequest):
    project_id = _ensure_default_project_id()
    session_id = _ensure_session_id(project_id, payload.session_id)
    mapped = AskRequest(
        question=payload.question,
        model=payload.model,
        fast=payload.fast,
        settings=payload.settings,
    )
    response = _stream_answer(project_id, session_id, mapped)
    response.headers["X-Session-Id"] = session_id
    return response

