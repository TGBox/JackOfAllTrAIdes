#!/usr/bin/env python3
"""Executable script to extract schema and sample rows from JSON, CSV, or SQL files."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.data_reducer import reduce_data_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reduce JSON, CSV, or SQL dumps into schemas and sample rows."
    )
    parser.add_argument("file", help="Path to JSON, CSV, or SQL data file")
    parser.add_argument(
        "-s", "--samples", type=int, default=3, help="Number of sample rows to keep (default: 3)"
    )
    parser.add_argument("-o", "--output", help="Optional output markdown file path")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[Fehler] Datei nicht gefunden: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = reduce_data_file(input_path, max_samples=args.samples)
    reduced = result["reduced_markdown"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(reduced, encoding="utf-8")
        print(f"✓ Reduziertes Schema gespeichert in: {out_p}")
        print(
            f"✓ Tokens: {result['original_tokens']:,} → {result['reduced_tokens']:,} (-{result['percentage_saved']}%)"
        )
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(reduced)


if __name__ == "__main__":
    main()
