import os
import sys
from pathlib import Path

# Add backend directory to path for clean imports
BACKEND_DIR = Path(__file__).parent.absolute()
ROOT_DIR = BACKEND_DIR.parent.absolute()
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from api.app import app
from config import get_settings

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    use_reload = settings.environment != "production"
    uvicorn.run(
        "main:app" if use_reload else app,
        host=settings.host,
        port=settings.port,
        reload=use_reload,
        log_level="debug" if settings.debug else "info",
    )
