import json
import os
from pathlib import Path
from time import perf_counter
from typing import Iterable, Optional

import requests
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from backend.llm.groq_client import (
    DEFAULT_GROQ_MODEL,
    generate_response as generate_response_groq,
    list_available_models as list_groq_models,
    resolve_model as resolve_groq_model,
    stream_response as stream_response_groq,
)
from backend.logging.logger import get_logger

if load_dotenv is not None:
    load_dotenv(dotenv_path=Path('.env'), override=True)


def _getenv(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, os.getenv(f"\ufeff{key}", default))


PRIMARY_MODEL = "llama3:8b"
FALLBACK_MODEL = "mistral:7b-instruct"
FAST_MODEL = "tinyllama"

OLLAMA_MODELS = [
    "llama3:8b",
    "mistral:7b-instruct",
    "deepseek-coder:6.7b",
    "tinyllama",
]

GROQ_MODEL_ALIASES = {
    "llama3:8b": None,
    "mistral:7b-instruct": None,
    "deepseek-coder:6.7b": None,
    "tinyllama": None,
}

ALLOWED_MODELS = set(
    OLLAMA_MODELS
    + [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        DEFAULT_GROQ_MODEL,
    ]
)

OLLAMA_URL = _getenv("OLLAMA_URL", "http://localhost:11434/api/generate") or "http://localhost:11434/api/generate"

DEFAULT_OPTIONS = {
    "num_predict": 256,
    "temperature": 0.3,
    "num_ctx": 2048,
}

logger = get_logger("llm-router")


def build_ollama_options(settings: Optional[dict], fast: bool = False) -> dict:
    options = dict(DEFAULT_OPTIONS)
    if not settings:
        if fast:
            options["num_predict"] = min(options["num_predict"], 128)
        return options

    temperature = settings.get("temperature")
    max_tokens = settings.get("max_tokens")

    if isinstance(temperature, (int, float)):
        options["temperature"] = max(0.0, min(1.0, float(temperature)))
    if isinstance(max_tokens, int):
        options["num_predict"] = max(32, min(2048, max_tokens))

    if fast:
        options["num_predict"] = min(options["num_predict"], 128)

    return options


def _provider() -> str:
    provider = (_getenv("LLM_PROVIDER", "ollama") or "ollama").strip().lower()
    if provider not in {"ollama", "groq"}:
        logger.info(f"Unknown LLM_PROVIDER='{provider}', defaulting to ollama")
        return "ollama"
    return provider


def _normalize_model(model: Optional[str]) -> str:
    if model in OLLAMA_MODELS:
        return model
    return PRIMARY_MODEL


def _model_chain(model: Optional[str], fast: bool) -> list[str]:
    chain = []
    if fast:
        chain.append(FAST_MODEL)
    if model:
        chain.append(_normalize_model(model))
    chain.extend([PRIMARY_MODEL, FALLBACK_MODEL])
    seen = set()
    deduped = []
    for item in chain:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def _call_ollama(model: str, prompt: str, options: Optional[dict] = None) -> str:
    t0 = perf_counter()
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options or DEFAULT_OPTIONS,
        },
        timeout=120,
    )
    response.raise_for_status()
    output = response.json().get("response", "")
    elapsed = perf_counter() - t0
    logger.info(f"Model inference: {elapsed:.2f}s (provider=ollama model={model})")
    return output


def _generate_with_ollama(
    prompt: str,
    model: Optional[str],
    fast: bool,
    options: Optional[dict],
) -> str:
    for candidate in _model_chain(model, fast):
        try:
            logger.info(f"Using provider=ollama model={candidate}")
            return _call_ollama(candidate, prompt, options=options)
        except Exception as exc:
            logger.error(f"Ollama model failed ({candidate}): {exc}")
            continue
    return "All models failed. Make sure Ollama is running (ollama serve)."


def _stream_with_ollama(
    prompt: str,
    model: Optional[str],
    fast: bool,
    options: Optional[dict],
) -> Iterable[str]:
    for candidate in _model_chain(model, fast):
        try:
            logger.info(f"Using provider=ollama model={candidate} stream=true")
            t0 = perf_counter()
            with requests.post(
                OLLAMA_URL,
                json={
                    "model": candidate,
                    "prompt": prompt,
                    "stream": True,
                    "options": options or DEFAULT_OPTIONS,
                },
                stream=True,
                timeout=120,
            ) as response:
                response.raise_for_status()
                buffer = ""
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    payload = json.loads(line)
                    token = payload.get("response", "")
                    if token:
                        buffer += token
                        if len(buffer) >= 32:
                            yield buffer
                            buffer = ""
                    if payload.get("done"):
                        if buffer:
                            yield buffer
                        elapsed = perf_counter() - t0
                        logger.info(
                            f"Model inference: {elapsed:.2f}s (provider=ollama model={candidate})"
                        )
                        return
            return
        except Exception as exc:
            logger.error(f"Ollama streaming failed ({candidate}): {exc}")
            continue

    yield "All models failed. Make sure Ollama is running (ollama serve)."


def _resolve_groq_model(model: Optional[str]) -> str:
    if model in GROQ_MODEL_ALIASES:
        return resolve_groq_model(GROQ_MODEL_ALIASES[model])
    return resolve_groq_model(model)


def _generate_with_groq(
    prompt: str,
    model: Optional[str],
    options: Optional[dict],
) -> str:
    selected_model = _resolve_groq_model(model)
    t0 = perf_counter()
    response = generate_response_groq(prompt=prompt, model=selected_model, options=options)
    elapsed = perf_counter() - t0
    logger.info(f"Model inference: {elapsed:.2f}s (provider=groq model={selected_model})")
    return response


def _stream_with_groq(
    prompt: str,
    model: Optional[str],
    options: Optional[dict],
) -> Iterable[str]:
    selected_model = _resolve_groq_model(model)
    t0 = perf_counter()
    for token in stream_response_groq(prompt=prompt, model=selected_model, options=options):
        yield token
    elapsed = perf_counter() - t0
    logger.info(f"Model inference: {elapsed:.2f}s (provider=groq model={selected_model})")


def get_llm_config() -> dict:
    provider = _provider()
    groq_models: list[str] = []
    try:
        groq_models = list_groq_models()
    except Exception:
        groq_models = [DEFAULT_GROQ_MODEL]

    deduped_groq = []
    seen = set()
    for model in groq_models:
        if model not in seen:
            seen.add(model)
            deduped_groq.append(model)

    return {
        "provider": provider,
        "models": {
            "ollama": OLLAMA_MODELS,
            "groq": deduped_groq or [DEFAULT_GROQ_MODEL],
        },
    }


def generate_response(
    prompt: str,
    model: Optional[str] = None,
    fast: bool = False,
    options: Optional[dict] = None,
) -> str:
    provider = _provider()
    if provider == "groq":
        try:
            return _generate_with_groq(prompt=prompt, model=model, options=options)
        except Exception as exc:
            logger.error(f"Groq failed, falling back to Ollama: {exc}")
            return _generate_with_ollama(prompt=prompt, model=model, fast=fast, options=options)

    return _generate_with_ollama(prompt=prompt, model=model, fast=fast, options=options)


def stream_response(
    prompt: str,
    model: Optional[str] = None,
    fast: bool = False,
    options: Optional[dict] = None,
) -> Iterable[str]:
    provider = _provider()
    if provider == "groq":
        try:
            for token in _stream_with_groq(prompt=prompt, model=model, options=options):
                yield token
            return
        except Exception as exc:
            logger.error(f"Groq streaming failed, falling back to Ollama: {exc}")
            for token in _stream_with_ollama(prompt=prompt, model=model, fast=fast, options=options):
                yield token
            return

    for token in _stream_with_ollama(prompt=prompt, model=model, fast=fast, options=options):
        yield token
