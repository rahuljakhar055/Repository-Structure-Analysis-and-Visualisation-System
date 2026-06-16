from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from .cache import get_cached_summary, set_cached_summary
except ImportError:
    from scanner.cache import get_cached_summary, set_cached_summary


MAX_CODE_CHARS = 12000


def summarize_file(root_path: str, relative_file_path: str) -> dict:
    root = Path(root_path).expanduser().resolve()
    file_path = (root / relative_file_path).resolve()

    try:
        file_path.relative_to(root)
    except ValueError as error:
        raise ValueError("File path must stay inside the scanned repository") from error

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    text = file_path.read_text(encoding="utf-8", errors="ignore")
    file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cache_key = f"{file_path}:{file_hash}"

    cached = get_cached_summary(cache_key)
    if cached:
        return {
            "filePath": relative_file_path,
            "hash": file_hash,
            "cached": True,
            "provider": cached.get("provider", "cache"),
            "summary": cached["summary"],
        }

    summary, provider = generate_summary(relative_file_path, text[:MAX_CODE_CHARS])
    cache_value = {
        "summary": summary,
        "provider": provider,
        "createdAt": int(time.time()),
    }
    set_cached_summary(cache_key, cache_value)

    return {
        "filePath": relative_file_path,
        "hash": file_hash,
        "cached": False,
        "provider": provider,
        "summary": summary,
    }


def generate_summary(relative_file_path: str, code_text: str) -> tuple[str, str]:
    if os.getenv("OPENAI_API_KEY"):
        return call_openai(relative_file_path, code_text), "openai"

    if os.getenv("GEMINI_API_KEY"):
        return call_gemini(relative_file_path, code_text), "gemini"

    return (
        "AI summary is not configured. Add OPENAI_API_KEY or GEMINI_API_KEY "
        "to the backend environment, restart the server, and click the file again.",
        "local-fallback",
    )


def call_openai(relative_file_path: str, code_text: str) -> str:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Explain source code clearly for a developer onboarding to a new project.",
            },
            {
                "role": "user",
                "content": build_prompt(relative_file_path, code_text),
            },
        ],
        "temperature": 0.2,
    }
    data = post_json(
        "https://api.openai.com/v1/chat/completions",
        payload,
        {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
    )
    return data["choices"][0]["message"]["content"].strip()


def call_gemini(relative_file_path: str, code_text: str) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    api_key = os.environ["GEMINI_API_KEY"]
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": build_prompt(relative_file_path, code_text),
                    }
                ]
            }
        ]
    }
    data = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        payload,
        {},
    )
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def build_prompt(relative_file_path: str, code_text: str) -> str:
    return (
        "Explain what this code does in 3 simple sentences.\n\n"
        f"File path: {relative_file_path}\n\n"
        "Code:\n"
        f"{code_text}"
    )


def post_json(url: str, payload: dict, headers: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            **headers,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AI API request failed: {detail}") from error
