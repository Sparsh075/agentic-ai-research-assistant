from __future__ import annotations

from pathlib import Path
from typing import Optional
import shutil

from fastapi import UploadFile

from .rag.rag_pipeline import RAGPipeline
from .storage.sqlite_store import SQLiteStore
from .app_logger.logger import get_logger


class ProjectManager:
    def __init__(
        self,
        store: Optional[SQLiteStore] = None,
        base_dir: str = "data/projects",
    ):
        self.store = store or SQLiteStore()
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._pipelines: dict[str, RAGPipeline] = {}
        self.logger = get_logger("project-manager")

    def _ensure_pipeline_loaded(self, project_id: str) -> RAGPipeline:
        pipeline = self._pipelines.get(project_id)
        if pipeline is not None:
            return pipeline

        pipeline = RAGPipeline()
        documents = self.store.list_documents(project_id)
        for doc in documents:
            try:
                pipeline.add_pdf(doc["path"])
            except Exception as exc:
                self.logger.error(f"Failed loading document {doc['path']}: {exc}")
        self._pipelines[project_id] = pipeline
        return pipeline

    def create_project(self, name: Optional[str] = None) -> dict:
        project = self.store.create_project(name or "New Project")
        (self.base_dir / project["id"]).mkdir(parents=True, exist_ok=True)
        return project

    def list_projects(self) -> list[dict]:
        return self.store.list_projects()

    def get_project(self, project_id: str) -> dict:
        project = self.store.get_project(project_id)
        if not project:
            raise KeyError("Project not found")
        return project

    def create_session(self, project_id: str, title: Optional[str], settings: dict) -> dict:
        self.get_project(project_id)
        return self.store.create_session(project_id, title or "New Session", settings)

    def list_sessions(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return self.store.list_sessions(project_id)

    def get_session(self, project_id: str, session_id: str) -> dict:
        self.get_project(project_id)
        session = self.store.get_session(session_id)
        if not session or session["project_id"] != project_id:
            raise KeyError("Session not found")
        session["messages"] = self.store.list_messages(session_id)
        return session

    def add_document(self, project_id: str, file: UploadFile) -> dict:
        self.get_project(project_id)

        filename = file.filename or "uploaded.pdf"
        project_dir = self.base_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        file_path = project_dir / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document = self.store.create_document(project_id, filename, str(file_path))
        pipeline = self._ensure_pipeline_loaded(project_id)
        pipeline.add_pdf(str(file_path))
        return document

    def list_documents(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return self.store.list_documents(project_id)

    def update_session_settings(self, session_id: str, settings: dict) -> None:
        self.store.update_session_settings(session_id, settings)

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[list[dict]] = None,
        diagnostics: Optional[dict] = None,
    ) -> dict:
        return self.store.add_message(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources or [],
            diagnostics=diagnostics or {},
        )

    def get_pipeline(self, project_id: str) -> RAGPipeline:
        self.get_project(project_id)
        return self._ensure_pipeline_loaded(project_id)


