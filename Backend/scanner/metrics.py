from __future__ import annotations

from pathlib import Path


COMMENT_PREFIXES = {
    ".py": ("#",),
    ".js": ("//",),
    ".jsx": ("//",),
    ".ts": ("//",),
    ".tsx": ("//",),
    ".c": ("//", "/*", "*"),
    ".h": ("//", "/*", "*"),
    ".cpp": ("//", "/*", "*"),
    ".hpp": ("//", "/*", "*"),
    ".java": ("//", "/*", "*"),
    ".css": ("/*", "*"),
    ".html": ("<!--",),
}

COMPLEXITY_WORDS = (
    "if ",
    "elif ",
    "else:",
    "for ",
    "while ",
    "case ",
    "catch ",
    "&&",
    "||",
    "?",
)


def calculate_metrics(file_path: str | Path) -> dict:
    path = Path(file_path)

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return {
            "totalLines": 0,
            "loc": 0,
            "blankLines": 0,
            "commentLines": 0,
            "complexity": 0,
        }

    extension = path.suffix.lower()
    prefixes = COMMENT_PREFIXES.get(extension, ())

    blank_lines = 0
    comment_lines = 0
    complexity = 1 if lines else 0

    for line in lines:
        stripped = line.strip()

        if not stripped:
            blank_lines += 1
            continue

        if prefixes and stripped.startswith(prefixes):
            comment_lines += 1

        complexity += sum(1 for word in COMPLEXITY_WORDS if word in stripped)

    total_lines = len(lines)
    loc = max(total_lines - blank_lines - comment_lines, 0)

    return {
        "totalLines": total_lines,
        "loc": loc,
        "blankLines": blank_lines,
        "commentLines": comment_lines,
        "complexity": complexity,
    }