import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path('.env'), override=True)


def _getenv(key: str, default: str | None = None) -> str | None:
    # Support .env files accidentally saved with UTF-8 BOM.
    return os.getenv(key, os.getenv(f"\ufeff{key}", default))


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    environment: str
    debug: bool
    host: str
    port: int
    cors_origins: list[str]
    cors_origin_regex: str | None


def get_settings() -> Settings:
    environment = (_getenv("ENVIRONMENT", "development") or "development").strip().lower()
    debug = _to_bool(_getenv("DEBUG"), default=False)
    if environment == "production":
        debug = False

    host = (_getenv("HOST", "0.0.0.0") or "0.0.0.0").strip() or "0.0.0.0"
    port = int(_getenv("PORT", "10000") or "10000")
    cors_origin_regex = _getenv("CORS_ORIGIN_REGEX")
    if not cors_origin_regex and environment == "production":
        cors_origin_regex = r"https://.*\.vercel\.app"

    return Settings(
        llm_provider=(_getenv("LLM_PROVIDER", "ollama") or "ollama").strip().lower() or "ollama",
        environment=environment,
        debug=debug,
        host=host,
        port=port,
        cors_origins=_parse_origins(_getenv("CORS_ORIGINS")),
        cors_origin_regex=cors_origin_regex,
    )
