"""Smart Dependency Context Collector: Recursively traces local module imports from an entrypoint file."""

import ast
from pathlib import Path
from typing import Any

from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens


def _find_local_imports(py_path: Path, project_root: Path) -> set[Path]:
    """Parse a python file and find referenced local project files."""
    if not py_path.is_file():
        return set()

    try:
        content = py_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()

    imported_paths: set[Path] = set()

    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                candidates.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            candidates.append(node.module)

        for cand in candidates:
            parts = cand.split(".")
            # Try matching relative to project_root
            candidate_file = project_root.joinpath(*parts).with_suffix(".py")
            if candidate_file.is_file() and candidate_file != py_path:
                imported_paths.add(candidate_file.resolve())
                continue

            # Try as a package __init__.py
            candidate_pkg = project_root.joinpath(*parts, "__init__.py")
            if candidate_pkg.is_file() and candidate_pkg != py_path:
                imported_paths.add(candidate_pkg.resolve())
                continue

            # Try matching relative to py_path's parent directory
            rel_file = py_path.parent.joinpath(*parts).with_suffix(".py")
            if rel_file.is_file() and rel_file != py_path:
                imported_paths.add(rel_file.resolve())

    return imported_paths


def trace_dependencies(
    entry_file: Path | str,
    project_root: Path | str | None = None,
    max_depth: int = 3,
) -> dict[str, Any]:
    """Recursively collect local project files imported by the entrypoint.

    Returns:
        dict with bundled markdown, list of traced files, and token count.
    """
    entry_path = Path(entry_file).resolve()
    if not entry_path.is_file():
        raise FileNotFoundError(f"Einstiegsdatei nicht gefunden: {entry_path}")

    root = Path(project_root).resolve() if project_root else entry_path.parent

    visited: set[Path] = {entry_path}
    queue: list[tuple[Path, int]] = [(entry_path, 0)]

    while queue:
        curr_path, depth = queue.pop(0)
        if depth >= max_depth:
            continue

        neighbors = _find_local_imports(curr_path, root)
        for neigh in neighbors:
            if neigh not in visited:
                visited.add(neigh)
                queue.append((neigh, depth + 1))

    # Build bundled Markdown context
    md_blocks: list[str] = [
        f"# Abhängigkeits-Kontext für `{entry_path.name}`",
        f"*Einstiegsdatei*: `{entry_path.relative_to(root).as_posix() if entry_path.is_relative_to(root) else entry_path.name}`",
        f"*Gefundene lokale Abhängigkeiten*: {len(visited)} Datei(en)",
        "",
    ]

    for p in sorted(visited):
        try:
            rel = p.relative_to(root).as_posix() if p.is_relative_to(root) else p.name
            code = p.read_text(encoding="utf-8", errors="ignore")
            md_blocks.append(f"## Datei: `{rel}`\n```python\n{code.strip()}\n```")
        except (OSError, UnicodeDecodeError):
            pass

    bundled_markdown = clean_markdown("\n\n".join(md_blocks))
    tokens = count_tokens(bundled_markdown)

    return {
        "entry_file": str(entry_path),
        "dependency_files": [str(p) for p in sorted(visited)],
        "bundled_markdown": bundled_markdown,
        "tokens": tokens,
    }
