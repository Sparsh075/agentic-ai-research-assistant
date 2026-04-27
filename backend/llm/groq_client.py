import os
import time
from pathlib import Path
from typing import Iterable, Optional

from app_logger.logger import get_logger

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path(".env"), override=False)


def _getenv(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, os.getenv(f"\ufeff{key}", default))


DEFAULT_GROQ_MODEL = _getenv("GROQ_MODEL", "llama-3.3-70b-versatile") or "llama-3.3-70b-versatile"
PREFERRED_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]
logger = get_logger("groq-client")
_MODEL_CACHE: dict[str, object] = {"ts": 0.0, "models": []}


def _get_client():
    try:
        from groq import Groq  # type: ignore
    except Exception as exc:
        raise RuntimeError("groq package is not installed. Run: pip install groq") from exc

    api_key = (_getenv("GROQ_API_KEY", "") or "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


def _build_params(prompt: str, model: Optional[str], options: Optional[dict]) -> dict:
    selected_model = resolve_model(model)
    temperature = 0.3
    max_tokens = 256

    if options:
        maybe_temp = options.get("temperature")
        maybe_tokens = options.get("num_predict") or options.get("max_tokens")
        if isinstance(maybe_temp, (int, float)):
            temperature = max(0.0, min(1.0, float(maybe_temp)))
        if isinstance(maybe_tokens, int):
            max_tokens = max(32, min(2048, int(maybe_tokens)))

    return {
        "model": selected_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def list_available_models(force_refresh: bool = False) -> list[str]:
    now = time.time()
    cached = _MODEL_CACHE.get("models", [])
    cache_ts = float(_MODEL_CACHE.get("ts", 0.0))
    if cached and not force_refresh and (now - cache_ts) < 300:
        return [str(item) for item in cached]

    client = _get_client()
    model_resp = client.models.list()
    models = [item.id for item in model_resp.data if getattr(item, "id", None)]
    _MODEL_CACHE["ts"] = now
    _MODEL_CACHE["models"] = models
    return models


def resolve_model(requested_model: Optional[str]) -> str:
    if requested_model:
        return requested_model

    try:
        available = set(list_available_models())
        for candidate in PREFERRED_GROQ_MODELS:
            if candidate in available:
                return candidate
    except Exception as exc:
        logger.error(f"Could not fetch Groq model list: {exc}")

    return DEFAULT_GROQ_MODEL


def generate_response(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[dict] = None,
) -> str:
    client = _get_client()
    params = _build_params(prompt=prompt, model=model, options=options)
    logger.info(f"Using provider=groq model={params['model']}")
    response = client.chat.completions.create(stream=False, **params)
    return (response.choices[0].message.content or "").strip()


def stream_response(
    prompt: str,
    model: Optional[str] = None,
    options: Optional[dict] = None,
) -> Iterable[str]:
    client = _get_client()
    params = _build_params(prompt=prompt, model=model, options=options)
    logger.info(f"Using provider=groq model={params['model']} stream=true")
    stream = client.chat.completions.create(stream=True, **params)

    for chunk in stream:
        token = ""
        if chunk.choices and chunk.choices[0].delta:
            token = chunk.choices[0].delta.content or ""
        if token:
            yield token

