#!/usr/bin/env python3
"""Executable script to package git diffs together with minimal structural file skeletons for code reviews."""

import argparse
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.modules.diff_packager import package_git_diff


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package git diffs with AST skeletons of modified files for focused code reviews."
    )
    parser.add_argument(
        "-r", "--repo", default=".", help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--staged", action="store_true", help="Include only staged changes (git diff --staged)"
    )
    parser.add_argument(
        "--no-skeletons", action="store_true", help="Omit AST interface skeletons of changed files"
    )
    parser.add_argument("-o", "--output", help="Optional output markdown file path")
    args = parser.parse_args()

    repo_dir = Path(args.repo).resolve()
    if not (repo_dir / ".git").exists():
        print(f"[Fehler] Kein Git-Repository gefunden in: {repo_dir}", file=sys.stderr)
        sys.exit(1)

    result = package_git_diff(
        repo_dir=repo_dir,
        staged=args.staged,
        include_skeletons=not args.no_skeletons,
    )

    packaged_md = result["packaged_markdown"]
    files = result["diff_files"]
    tokens = result["tokens"]

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(packaged_md, encoding="utf-8")
        print(f"✓ Diff-Paket gespeichert in: {out_p}")
        print(f"✓ {len(files)} geänderte Datei(en) gepackt ({tokens:,} Tokens)")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(packaged_md)


if __name__ == "__main__":
    main()
