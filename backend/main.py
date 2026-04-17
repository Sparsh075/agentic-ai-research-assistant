import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
for path in (CURRENT_DIR, ROOT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.api.app import app
from backend.config import get_settings

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment != "production",
        log_level="debug" if settings.debug else "info",
    )
