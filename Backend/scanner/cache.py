from __future__ import annotations

import json
from pathlib import Path


CACHE_FILE = Path(__file__).resolve().parents[1] / ".cache" / "ai_summaries.json"


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}

    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def get_cached_summary(cache_key: str) -> dict | None:
    return load_cache().get(cache_key)


def set_cached_summary(cache_key: str, value: dict) -> None:
    cache = load_cache()
    cache[cache_key] = value

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")