from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional
from uuid import uuid4
from datetime import datetime


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


class SQLiteStore:
    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    settings_json TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    diagnostics_json TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    path TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                );
                """
            )

    def create_project(self, name: str) -> dict:
        project_id = str(uuid4())
        created_at = _now_iso()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO projects (id, name, created_at) VALUES (?, ?, ?)",
                (project_id, name, created_at),
            )
        return {"id": project_id, "name": name, "created_at": created_at}

    def list_projects(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM projects ORDER BY created_at ASC").fetchall()
            results = []
            for row in rows:
                pid = row["id"]
                session_count = conn.execute(
                    "SELECT COUNT(*) FROM sessions WHERE project_id = ?",
                    (pid,),
                ).fetchone()[0]
                document_count = conn.execute(
                    "SELECT COUNT(*) FROM documents WHERE project_id = ?",
                    (pid,),
                ).fetchone()[0]
                results.append(
                    {
                        "id": pid,
                        "name": row["name"],
                        "created_at": row["created_at"],
                        "session_count": session_count,
                        "document_count": document_count,
                    }
                )
            return results

    def get_project(self, project_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
            }

    def create_session(self, project_id: str, title: str, settings: dict) -> dict:
        session_id = str(uuid4())
        created_at = _now_iso()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sessions (id, project_id, title, created_at, settings_json) VALUES (?, ?, ?, ?, ?)",
                (session_id, project_id, title, created_at, json.dumps(settings)),
            )
        return {
            "id": session_id,
            "project_id": project_id,
            "title": title,
            "created_at": created_at,
            "settings": settings,
        }

    def list_sessions(self, project_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE project_id = ? ORDER BY created_at ASC",
                (project_id,),
            ).fetchall()
            results = []
            for row in rows:
                msg_count = conn.execute(
                    "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                    (row["id"],),
                ).fetchone()[0]
                results.append(
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "created_at": row["created_at"],
                        "message_count": msg_count,
                    }
                )
            return results

    def get_session(self, session_id: str) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "project_id": row["project_id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "settings": json.loads(row["settings_json"]),
            }

    def update_session_settings(self, session_id: str, settings: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET settings_json = ? WHERE id = ?",
                (json.dumps(settings), session_id),
            )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[list[dict]] = None,
        diagnostics: Optional[dict] = None,
    ) -> dict:
        ts = _now_iso()
        src = sources or []
        diag = diagnostics or {}
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp, sources_json, diagnostics_json) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, role, content, ts, json.dumps(src), json.dumps(diag)),
            )
            mid = cursor.lastrowid
        return {
            "id": mid,
            "session_id": session_id,
            "role": role,
            "content": content,
            "ts": ts,
            "sources": src,
            "diagnostics": diag,
        }

    def list_messages(self, session_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC",
                (session_id,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "role": row["role"],
                    "content": row["content"],
                    "ts": row["timestamp"],
                    "sources": json.loads(row["sources_json"]),
                    "diagnostics": json.loads(row["diagnostics_json"]),
                }
                for row in rows
            ]

    def create_document(self, project_id: str, filename: str, path: str) -> dict:
        did = str(uuid4())
        ts = _now_iso()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO documents (id, project_id, filename, path, uploaded_at) VALUES (?, ?, ?, ?, ?)",
                (did, project_id, filename, path, ts),
            )
        return {"id": did, "project_id": project_id, "filename": filename, "path": path, "uploaded_at": ts}

    def list_documents(self, project_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM documents WHERE project_id = ? ORDER BY uploaded_at ASC",
                (project_id,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "project_id": row["project_id"],
                    "filename": row["filename"],
                    "path": row["path"],
                    "uploaded_at": row["uploaded_at"],
                }
                for row in rows
            ]
