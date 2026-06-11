from __future__ import annotations

import ast
import re
from pathlib import Path


PYTHON_EXTENSIONS = {".py"}
C_LIKE_EXTENSIONS = {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx"}
JS_LIKE_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}

INCLUDE_PATTERN = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]')
JS_IMPORT_PATTERN = re.compile(
    r"""(?:import\s+.*?\s+from\s+|import\s*\(|require\s*\()\s*['"]([^'"]+)['"]"""
)


def parse_dependencies(file_path: str | Path) -> list[dict]:
    """Parse a source file and return dependency names without running code."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in PYTHON_EXTENSIONS:
        return parse_python_dependencies(path)

    if extension in C_LIKE_EXTENSIONS:
        return parse_c_like_dependencies(path)

    if extension in JS_LIKE_EXTENSIONS:
        return parse_js_like_dependencies(path)

    return []


def parse_python_dependencies(path: Path) -> list[dict]:
    text = read_text_safely(path)

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    dependencies = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.append(
                    {
                        "name": alias.name,
                        "type": "python-import",
                        "line": node.lineno,
                    }
                )

        if isinstance(node, ast.ImportFrom):
            module_name = "." * node.level + (node.module or "")
            dependencies.append(
                {
                    "name": module_name,
                    "type": "python-from-import",
                    "line": node.lineno,
                }
            )

    return dependencies


def parse_c_like_dependencies(path: Path) -> list[dict]:
    dependencies = []

    for line_number, line in enumerate(read_text_safely(path).splitlines(), start=1):
        match = INCLUDE_PATTERN.match(line)

        if match:
            dependencies.append(
                {
                    "name": match.group(1),
                    "type": "c-include",
                    "line": line_number,
                }
            )

    return dependencies


def parse_js_like_dependencies(path: Path) -> list[dict]:
    dependencies = []

    for line_number, line in enumerate(read_text_safely(path).splitlines(), start=1):
        for match in JS_IMPORT_PATTERN.finditer(line):
            dependencies.append(
                {
                    "name": match.group(1),
                    "type": "javascript-import",
                    "line": line_number,
                }
            )

    return dependencies


def read_text_safely(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")