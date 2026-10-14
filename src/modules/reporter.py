"""Project Architecture & Codebase Reporter: Generates compact Markdown overviews of repositories."""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.gitignore import GitIgnoreMatcher
from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens, estimate_token_cost
from src.modules.skeletonizer import skeletonize_code

IMPORT_PY_REGEX = re.compile(
    r"^(?:from\s+([a-zA-Z0-9_\.]+)|import\s+([a-zA-Z0-9_\.]+))", re.MULTILINE
)
IMPORT_JS_REGEX = re.compile(
    r"""(?:import\s+.*?from\s+['"]([^'"]+)['"]|require\(['"]([^'"]+)['"]\))"""
)


@dataclass
class FileStat:
    path: Path
    rel_path: str
    size_bytes: int
    tokens: int
    lines: int


def _scan_repository_files(root_dir: Path) -> list[FileStat]:
    """Scan all non-ignored text files in repository and collect stats."""
    matcher = GitIgnoreMatcher(root_dir)
    file_stats: list[FileStat] = []

    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if matcher.is_ignored(path):
            continue

        try:
            size = path.stat().st_size
            # Skip massive binary files (> 5MB)
            if size > 5 * 1024 * 1024:
                continue

            content = path.read_text(encoding="utf-8", errors="ignore")
            # Heuristic check for binary files (e.g. null bytes)
            if "\x00" in content:
                continue

            lines = len(content.splitlines())
            tokens = count_tokens(content)
            rel_str = path.relative_to(root_dir).as_posix()
            file_stats.append(
                FileStat(path=path, rel_path=rel_str, size_bytes=size, tokens=tokens, lines=lines)
            )
        except (OSError, UnicodeDecodeError):
            continue

    return file_stats


def _build_ascii_tree(file_stats: list[FileStat], max_entries: int = 40) -> str:
    """Generate an organized tree structure of scanned files."""
    paths = sorted([f.rel_path for f in file_stats])
    if len(paths) > max_entries:
        sample_paths = paths[:max_entries]
        tree_lines = [f"- {p}" for p in sample_paths]
        tree_lines.append(f"- ... und {len(paths) - max_entries} weitere Dateien")
    else:
        tree_lines = [f"- {p}" for p in paths]
    return "\n".join(tree_lines)


def _extract_dependencies(
    file_stats: list[FileStat],
) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """Extract top internal and third-party imports across codebase."""
    imports_counter: Counter[str] = Counter()

    for stat in file_stats:
        ext = stat.path.suffix.lower()
        if ext == ".py":
            try:
                content = stat.path.read_text(encoding="utf-8", errors="ignore")
                for match in IMPORT_PY_REGEX.finditer(content):
                    mod = (match.group(1) or match.group(2) or "").split(".")[0]
                    if mod:
                        imports_counter[mod] += 1
            except (OSError, UnicodeDecodeError):
                pass
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            try:
                content = stat.path.read_text(encoding="utf-8", errors="ignore")
                for match in IMPORT_JS_REGEX.finditer(content):
                    pkg = match.group(1) or match.group(2) or ""
                    if pkg and not pkg.startswith("."):
                        imports_counter[pkg.split("/")[0]] += 1
            except (OSError, UnicodeDecodeError):
                pass

    top_deps = imports_counter.most_common(15)
    return top_deps, []


def generate_project_report(
    project_dir: Path | str,
    include_skeletons: bool = False,
    max_skeleton_files: int = 5,
) -> dict[str, Any]:
    """Analyze a project repository and generate a compact architecture overview."""
    root = Path(project_dir).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Projektverzeichnis existiert nicht: {root}")

    file_stats = _scan_repository_files(root)
    total_files = len(file_stats)
    total_lines = sum(f.lines for f in file_stats)
    total_tokens = sum(f.tokens for f in file_stats)
    total_cost = estimate_token_cost(total_tokens, "claude-3-5-sonnet")

    # Top token consumers
    top_consumers = sorted(file_stats, key=lambda f: f.tokens, reverse=True)[:10]

    # Dependencies
    top_deps, _ = _extract_dependencies(file_stats)

    # Tree
    tree_view = _build_ascii_tree(file_stats)

    report_lines: list[str] = [
        f"# Projekt-Architektur-Report: `{root.name}`",
        "",
        "## 1. Kennzahlen & Token-Budget",
        f"- **Analysierte Dateien**: {total_files}",
        f"- **Gesamte Codezeilen (LOC)**: {total_lines:,}",
        f"- **Gesamter Token-Bedarf**: {total_tokens:,} Tokens",
        f"- **Geschätzte Input-Kosten (Claude 3.5 Sonnet)**: ~${total_cost:.4f}",
        "",
        "## 2. Top-Token-Verbraucher (Größte Dateien)",
        "| Datei | Zeilen | Tokens | % vom Gesamtprojekt |",
        "|---|---|---|---|",
    ]

    for f in top_consumers:
        pct = (f.tokens / total_tokens * 100.0) if total_tokens > 0 else 0.0
        report_lines.append(f"| `{f.rel_path}` | {f.lines:,} | {f.tokens:,} | {pct:.1f}% |")

    report_lines.extend(
        [
            "",
            "## 3. Erkannte Abhängigkeiten & Module",
        ]
    )

    if top_deps:
        dep_items = [f"- `{dep}` ({count}x importiert)" for dep, count in top_deps]
        report_lines.append("\n".join(dep_items))
    else:
        report_lines.append("*Keine externen Abhängigkeiten oder Importe identifiziert.*")

    report_lines.extend(
        [
            "",
            "## 4. Bereinigter Dateibaum (.gitignore berücksichtigt)",
            "```text",
            tree_view,
            "```",
        ]
    )

    if include_skeletons:
        py_files = [f for f in file_stats if f.path.suffix.lower() == ".py"][:max_skeleton_files]
        if py_files:
            report_lines.extend(
                [
                    "",
                    "## 5. API-Skelette zentraler Python-Komponenten (ohne Rümpfe)",
                ]
            )
            for py_stat in py_files:
                try:
                    src = py_stat.path.read_text(encoding="utf-8", errors="ignore")
                    skeleton = skeletonize_code(src, keep_docstrings=True)
                    report_lines.extend(
                        [
                            f"### `{py_stat.rel_path}`",
                            "```python",
                            skeleton,
                            "```",
                        ]
                    )
                except (OSError, UnicodeDecodeError):
                    pass

    markdown_report = clean_markdown("\n".join(report_lines))

    return {
        "project_name": root.name,
        "total_files": total_files,
        "total_tokens": total_tokens,
        "total_lines": total_lines,
        "estimated_cost_usd": total_cost,
        "top_consumers": [
            {"path": f.rel_path, "tokens": f.tokens, "lines": f.lines} for f in top_consumers
        ],
        "markdown": markdown_report,
    }
