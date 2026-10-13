#!/usr/bin/env python3
"""Executable script to sanitize and compress error logs, stack traces, and terminal dumps."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.log_compressor import compress_log_file, compress_logs


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanitize and compress logs and stacktraces.")
    parser.add_argument("file", nargs="?", help="Path to log file (or stdin if omitted)")
    parser.add_argument("-o", "--output", help="Optional output markdown file path")
    args = parser.parse_args()

    if args.file:
        input_path = Path(args.file)
        if not input_path.is_file():
            print(f"[Fehler] Datei nicht gefunden: {input_path}", file=sys.stderr)
            sys.exit(1)
        result = compress_log_file(input_path)
        compressed = result["compressed_log"]
        orig_tok = result["original_tokens"]
        comp_tok = result["reduced_tokens"]
        pct = result["percentage_saved"]
    else:
        # Read from stdin
        raw_text = sys.stdin.read()
        compressed = compress_logs(raw_text)
        orig_tok = len(raw_text) // 4
        comp_tok = len(compressed) // 4
        pct = round(max(0, orig_tok - comp_tok) / orig_tok * 100, 1) if orig_tok else 0.0

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(compressed, encoding="utf-8")
        print(f"✓ Bereinigter Log gespeichert in: {out_p}")
        print(f"✓ Tokens: {orig_tok:,} → {comp_tok:,} (-{pct}%)")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(compressed)


if __name__ == "__main__":
    main()
