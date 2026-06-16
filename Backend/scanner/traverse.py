from __future__ import annotations

import os
from pathlib import Path

try:
    from .parser import parse_dependencies
except ImportError:
    from scanner.parser import parse_dependencies


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "venv",
    ".venv",
    "env",
    ".repo_visualizer_cache",
}

IGNORED_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
}

FILE_TYPES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "react",
    ".ts": "typescript",
    ".tsx": "react-typescript",
    ".java": "java",
    ".c": "c",
    ".h": "c-header",
    ".cpp": "cpp",
    ".hpp": "cpp-header",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".md": "markdown",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
}


def get_file_type(path: Path) -> str:
    return FILE_TYPES.get(path.suffix.lower(), "unknown")


def should_ignore_dir(path: Path) -> bool:
    return path.name in IGNORED_DIRS


def should_ignore_file(path: Path) -> bool:
    return path.name in IGNORED_FILES or path.suffix.lower() in IGNORED_EXTENSIONS


def scan_repository(root_path: str | Path) -> dict:
    root = Path(root_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    files = []

    for current_dir_raw, dir_names, file_names in os.walk(root):
        current_dir = Path(current_dir_raw)

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not should_ignore_dir(current_dir / dir_name)
        ]

        for file_name in file_names:
            file_path = current_dir / file_name

            if should_ignore_file(file_path):
                continue

            try:
                relative_path = file_path.relative_to(root).as_posix()
                dependencies = parse_dependencies(file_path)
                size_bytes = file_path.stat().st_size
            except OSError:
                continue

            files.append(
                {
                    "id": relative_path,
                    "name": file_path.name,
                    "path": relative_path,
                    "extension": file_path.suffix.lower(),
                    "type": get_file_type(file_path),
                    "sizeBytes": size_bytes,
                    "dependencyCount": len(dependencies),
                    "dependencies": dependencies,
                }
            )

    files.sort(key=lambda item: item["path"].lower())

    return {
        "root": str(root),
        "totalFiles": len(files),
        "files": files,
    }
