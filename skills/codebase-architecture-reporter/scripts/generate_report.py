#!/usr/bin/env python3
"""Executable script to analyze a codebase and generate a compact architecture overview."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.reporter import generate_project_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate compact architecture overview of a codebase."
    )
    parser.add_argument(
        "dir", nargs="?", default=".", help="Project directory to scan (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", help="Optional output markdown file path (e.g. PROJECT_OVERVIEW.md)"
    )
    parser.add_argument(
        "-s", "--skeletons", action="store_true", help="Embed API skeletons of key Python modules"
    )
    parser.add_argument(
        "--max-skeletons",
        type=int,
        default=5,
        help="Maximum number of skeletonized files (default: 5)",
    )
    args = parser.parse_args()

    target_dir = Path(args.dir).resolve()
    if not target_dir.is_dir():
        print(f"[Fehler] Verzeichnis nicht gefunden: {target_dir}", file=sys.stderr)
        sys.exit(1)

    result = generate_project_report(
        target_dir,
        include_skeletons=args.skeletons,
        max_skeleton_files=args.max_skeletons,
    )
    markdown = result["markdown"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(markdown, encoding="utf-8")
        print(f"✓ Architektur-Report gespeichert in: {out_p}")
        print(
            f"✓ Analysierte Dateien: {result['total_files']} | Tokens: {result['total_tokens']:,}"
        )
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(markdown)


if __name__ == "__main__":
    main()
