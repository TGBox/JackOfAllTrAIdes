#!/usr/bin/env python3
"""Executable script to recursively trace local module imports and bundle them into an LLM context."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.dep_tracer import trace_dependencies


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recursively collect local project dependencies starting from an entry point."
    )
    parser.add_argument(
        "entry", help="Path to Python entrypoint file (e.g., main.py or a test file)"
    )
    parser.add_argument(
        "-r", "--root", help="Project root directory (defaults to entry file's directory)"
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=3,
        help="Max recursion depth for import tracing (default: 3)",
    )
    parser.add_argument("-o", "--output", help="Optional output markdown file path")
    args = parser.parse_args()

    entry_path = Path(args.entry)
    if not entry_path.is_file():
        print(f"[Fehler] Datei nicht gefunden: {entry_path}", file=sys.stderr)
        sys.exit(1)

    result = trace_dependencies(
        entry_file=entry_path,
        project_root=args.root,
        max_depth=args.depth,
    )

    bundled_md = result["bundled_markdown"]
    files = result["files"]
    total_tokens = result["total_tokens"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(bundled_md, encoding="utf-8")
        print(f"✓ Abhängigkeits-Kontext gespeichert in: {out_p}")
        print(f"✓ {len(files)} Datei(en) gebündelt ({total_tokens:,} Tokens)")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(bundled_md)


if __name__ == "__main__":
    main()
