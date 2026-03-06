from pydantic import BaseModel
from typing import Optional


class SessionSettings(BaseModel):
    temperature: float = 0.3
    max_tokens: int = 256
    rag_enabled: bool = True
    top_k: int = 3
    fast_mode: bool = False


class ProjectCreateRequest(BaseModel):
    name: Optional[str] = None


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class AskRequest(BaseModel):
    question: str
    model: Optional[str] = None
    fast: Optional[bool] = False
    settings: Optional[SessionSettings] = None


class LegacyAskRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    model: Optional[str] = None
    fast: Optional[bool] = False
    settings: Optional[SessionSettings] = None
