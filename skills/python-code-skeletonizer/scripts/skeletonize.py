#!/usr/bin/env python3
"""Executable script to extract Python AST interfaces without function bodies."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.skeletonizer import skeletonize_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Python AST interface skeletons.")
    parser.add_argument("file", help="Path to Python file (.py)")
    parser.add_argument("-o", "--output", help="Optional output file path")
    parser.add_argument(
        "--no-docstrings", action="store_true", help="Omit docstrings for extreme compression"
    )
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[Fehler] Datei nicht gefunden: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = skeletonize_file(input_path, keep_docstrings=not args.no_docstrings)
    skeleton = result["skeleton"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(skeleton, encoding="utf-8")
        print(f"✓ Skelett gespeichert in: {out_p}")
        print(
            f"✓ Tokens: {result['original_tokens']:,} → {result['reduced_tokens']:,} (-{result['percentage_saved']}%)"
        )
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(skeleton)


if __name__ == "__main__":
    main()
