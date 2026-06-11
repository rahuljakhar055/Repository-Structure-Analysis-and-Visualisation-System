from __future__ import annotations

from pathlib import Path, PurePosixPath

from .metrics import calculate_metrics
from .traverse import scan_repository


JS_EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def build_repository_graph(root_path: str | Path) -> dict:
    scan_result = scan_repository(root_path)
    root = Path(scan_result["root"])
    files = scan_result["files"]
    module_index = build_module_index(files)
    file_paths = {file_item["path"] for file_item in files}

    nodes = []
    edges = []

    for index, file_item in enumerate(files):
        metrics = calculate_metrics(root / file_item["path"])
        file_item["metrics"] = metrics

        nodes.append(
            {
                "id": file_item["path"],
                "position": {
                    "x": (index % 4) * 280,
                    "y": (index // 4) * 160,
                },
                "data": {
                    "label": f"{file_item['name']} ({metrics['loc']} LoC)",
                    "name": file_item["name"],
                    "path": file_item["path"],
                    "type": file_item["type"],
                    "loc": metrics["loc"],
                    "complexity": metrics["complexity"],
                    "dependencyCount": file_item["dependencyCount"],
                },
            }
        )

        for dependency in file_item["dependencies"]:
            target_path = resolve_dependency(file_item, dependency, module_index, file_paths)

            if target_path and target_path != file_item["path"]:
                edge_id = f"{file_item['path']}->{target_path}:{dependency['line']}"
                edges.append(
                    {
                        "id": edge_id,
                        "source": file_item["path"],
                        "target": target_path,
                        "label": dependency["name"],
                    }
                )

    return {
        "root": scan_result["root"],
        "totalFiles": scan_result["totalFiles"],
        "nodes": nodes,
        "edges": edges,
        "files": files,
    }


def build_module_index(files: list[dict]) -> dict[str, str]:
    index = {}

    for file_item in files:
        path = file_item["path"]
        pure_path = PurePosixPath(path)
        extension = pure_path.suffix.lower()

        add_index_key(index, pure_path.name, path)

        if extension == ".py":
            module = str(pure_path.with_suffix("")).replace("/", ".")
            add_module_variants(index, module, path)

            if pure_path.name == "__init__.py":
                package = str(pure_path.parent).replace("/", ".")
                add_module_variants(index, package, path)

        if extension in JS_EXTENSIONS:
            module = str(pure_path.with_suffix("")).replace("/", ".")
            add_module_variants(index, module, path)

    return index


def add_module_variants(index: dict[str, str], module: str, path: str) -> None:
    parts = [part for part in module.split(".") if part and part != "__init__"]

    for start in range(len(parts)):
        add_index_key(index, ".".join(parts[start:]), path)


def add_index_key(index: dict[str, str], key: str, path: str) -> None:
    if key and key not in index:
        index[key] = path


def resolve_dependency(
    source_file: dict,
    dependency: dict,
    module_index: dict[str, str],
    file_paths: set[str],
) -> str | None:
    dependency_name = dependency["name"]

    if dependency_name.startswith("."):
        return resolve_relative_python_import(source_file["path"], dependency_name, module_index)

    if dependency_name.startswith("./") or dependency_name.startswith("../"):
        return resolve_relative_js_import(source_file["path"], dependency_name, file_paths)

    return module_index.get(dependency_name)


def resolve_relative_python_import(
    source_path: str,
    dependency_name: str,
    module_index: dict[str, str],
) -> str | None:
    level = len(dependency_name) - len(dependency_name.lstrip("."))
    module_tail = dependency_name[level:]

    source_module_parts = list(PurePosixPath(source_path).with_suffix("").parent.parts)
    base_length = max(len(source_module_parts) - level + 1, 0)
    base_parts = source_module_parts[:base_length]

    if module_tail:
        base_parts.extend(module_tail.split("."))

    return module_index.get(".".join(base_parts))


def resolve_relative_js_import(
    source_path: str,
    dependency_name: str,
    file_paths: set[str],
) -> str | None:
    source_dir = PurePosixPath(source_path).parent
    base_path = source_dir / dependency_name

    candidates = [str(base_path)]

    for extension in JS_EXTENSIONS:
        candidates.append(f"{base_path}{extension}")
        candidates.append(str(base_path / f"index{extension}"))

    for candidate in candidates:
        normalized = str(PurePosixPath(candidate))
        if normalized in file_paths:
            return normalized

    return None
