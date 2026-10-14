"""Git Diff Context Packager: Combines git diffs with structural interfaces of modified files."""

import re
import subprocess
from pathlib import Path
from typing import Any

from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens
from src.modules.skeletonizer import skeletonize_code

DIFF_FILE_REGEX = re.compile(r"^\s*diff --git a/(.*?)\s+b/(.*?)\s*$", re.MULTILINE)


def get_git_diff(repo_dir: Path | str, staged: bool = False) -> str:
    """Run git diff command in repository directory."""
    cmd = ["git", "diff", "--staged"] if staged else ["git", "diff"]
    try:
        res = subprocess.run(
            cmd,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False,
        )
        return res.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def package_git_diff(
    repo_dir: Path | str,
    raw_diff: str | None = None,
    staged: bool = False,
    include_skeletons: bool = True,
) -> dict[str, Any]:
    """Package git diff together with skeletons of affected files for review or debugging."""
    root = Path(repo_dir).resolve()
    diff_text = raw_diff if raw_diff is not None else get_git_diff(root, staged=staged)

    if not diff_text.strip():
        empty_msg = "*Keine ungespeicherten oder geänderten Git-Änderungen gefunden.*"
        return {
            "diff_files": [],
            "packaged_markdown": empty_msg,
            "tokens": count_tokens(empty_msg),
        }

    # Find modified file names from git diff
    matches = DIFF_FILE_REGEX.findall(diff_text)
    affected_files = sorted({m[1] for m in matches})

    md_blocks: list[str] = [
        f"# Git-Diff Kontext-Paket: `{root.name}`",
        f"*Status*: {'Staged Changes (--staged)' if staged else 'Working Tree Changes'}",
        f"*Betroffene Dateien ({len(affected_files)})*:",
    ]
    for af in affected_files:
        md_blocks.append(f"- `{af}`")

    if include_skeletons:
        skeleton_blocks: list[str] = ["## Schnittstellen der betroffenen Dateien"]
        for af in affected_files:
            file_path = root / af
            if file_path.is_file() and file_path.suffix.lower() == ".py":
                try:
                    src = file_path.read_text(encoding="utf-8", errors="ignore")
                    skel = skeletonize_code(src, keep_docstrings=True)
                    skeleton_blocks.append(f"### `{af}` (Schnittstelle)\n```python\n{skel}\n```")
                except (OSError, UnicodeDecodeError):
                    pass
        if len(skeleton_blocks) > 1:
            md_blocks.extend(skeleton_blocks)

    md_blocks.append("## Vollständiger Git-Diff\n```diff\n" + diff_text.strip() + "\n```")

    packaged = clean_markdown("\n\n".join(md_blocks))
    tokens = count_tokens(packaged)

    return {
        "diff_files": affected_files,
        "packaged_markdown": packaged,
        "tokens": tokens,
    }
