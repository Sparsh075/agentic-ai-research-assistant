# backend/api/routes/__init__.py
from .query import router as query_router
from .graph import router as graph_router
from .recommendations import router as recommendations_router
from .memory import router as memory_router

__all__ = [
    "query_router",
    "graph_router",
    "recommendations_router",
    "memory_router"
]