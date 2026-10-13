#!/usr/bin/env python3
"""Executable script to convert PDF, DOCX, HTML, or IPYNB to clean Markdown."""

import argparse
import sys
from pathlib import Path

# Ensure src can be imported if running within repo
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

try:
    from src.modules.converter import convert_to_markdown
except ImportError:
    # Standalone fallback if invoked outside repo
    from pypdf import PdfReader

    def convert_to_markdown(file_path: Path | str, include_outputs: bool = False):
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            pages = [
                f"## Seite {i + 1}\n\n{p.extract_text() or ''}" for i, p in enumerate(reader.pages)
            ]
            return {
                "markdown": "\n\n---\n\n".join(pages),
                "file_name": path.name,
                "reduced_tokens": 100,
            }
        return {
            "markdown": path.read_text(errors="ignore"),
            "file_name": path.name,
            "reduced_tokens": 100,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert documents to token-efficient Markdown.")
    parser.add_argument("file", help="Path to PDF, DOCX, HTML, or IPYNB file")
    parser.add_argument("-o", "--output", help="Optional output markdown file path")
    parser.add_argument(
        "--include-outputs", action="store_true", help="Include cell outputs for notebooks"
    )
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.is_file():
        print(f"[Fehler] Datei nicht gefunden: {input_path}", file=sys.stderr)
        sys.exit(1)

    result = convert_to_markdown(input_path, include_outputs=args.include_outputs)
    markdown = result["markdown"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(markdown, encoding="utf-8")
        print(f"✓ Konvertiert nach: {out_p}")
        if "tokens_saved" in result:
            print(
                f"✓ Tokens eingespart: {result['tokens_saved']:,} (-{result.get('percentage_saved', 0)}%)"
            )
    else:
        # Setup stdout encoding
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(markdown)


if __name__ == "__main__":
    main()
