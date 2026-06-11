from pathlib import Path
import os


IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "dist",
    "build",
}

FILE_TYPES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "react",
    ".ts": "typescript",
    ".tsx": "react-typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c-header",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".md": "markdown",
}


def get_file_type(file_path: Path) -> str:
    return FILE_TYPES.get(file_path.suffix.lower(), "unknown")


def scan_repository(root_path: str) -> dict:
    root = Path(root_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")

    files = []

    for current_dir, dir_names, file_names in os.walk(root):
        current_path = Path(current_dir)

        dir_names[:] = [
            directory
            for directory in dir_names
            if directory not in IGNORED_DIRS
        ]

        for file_name in file_names:
            file_path = current_path / file_name
            relative_path = file_path.relative_to(root).as_posix()

            files.append({
                "id": relative_path,
                "name": file_path.name,
                "path": relative_path,
                "extension": file_path.suffix,
                "type": get_file_type(file_path),
                "sizeBytes": file_path.stat().st_size,
            })

    return {
        "root": str(root),
        "totalFiles": len(files),
        "files": files,
    }