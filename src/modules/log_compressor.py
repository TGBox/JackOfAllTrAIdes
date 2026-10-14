import re
from pathlib import Path
from typing import Any

from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens

# Regex to strip ANSI escape codes
ANSI_ESCAPE_REGEX = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Detect virtualenv or site-packages or node_modules frames
FRAMEWORK_FRAME_PYTHON = re.compile(
    r'^\s*File\s+"(?:.*?site-packages.*?|.*?lib[\\/]python.*?|.*?<frozen.*?>)"', re.IGNORECASE
)
FRAMEWORK_FRAME_NODE = re.compile(r"^\s*at\s+.*?(?:node_modules|[\\/]node:).*?\(", re.IGNORECASE)


def strip_ansi_codes(text: str) -> str:
    """Remove terminal color and formatting escape sequences."""
    return ANSI_ESCAPE_REGEX.sub("", text)


def compress_logs(raw_logs: str, max_repeated_lines: int = 2) -> str:
    """Compress verbose logs and stacktraces to retain only essential diagnostic information.

    Args:
        raw_logs: Unprocessed terminal output or log file content.
        max_repeated_lines: Maximum consecutive identical lines before folding.

    Returns:
        Token-efficient Markdown diagnostic summary.
    """
    cleaned = strip_ansi_codes(raw_logs)
    lines = cleaned.splitlines()
    if not lines:
        return "*Keine Log-Einträge vorhanden.*"

    # Step 1: Collapse repetitive lines
    deduped_lines: list[str] = []
    repeat_count = 1

    for i in range(len(lines)):
        curr = lines[i].strip()
        prev = lines[i - 1].strip() if i > 0 else None

        if curr and curr == prev:
            repeat_count += 1
            if repeat_count <= max_repeated_lines:
                deduped_lines.append(lines[i])
        else:
            if repeat_count > max_repeated_lines:
                deduped_lines.append(
                    f"    ... [Zeile {repeat_count - max_repeated_lines}x wiederholt ausgelassen]"
                )
            repeat_count = 1
            deduped_lines.append(lines[i])

    if repeat_count > max_repeated_lines:
        deduped_lines.append(
            f"    ... [Zeile {repeat_count - max_repeated_lines}x wiederholt ausgelassen]"
        )

    # Step 2: Collapse framework frames in tracebacks
    pruned_lines: list[str] = []
    skipped_framework_frames = 0
    in_python_traceback = False

    for line in deduped_lines:
        if "Traceback (most recent call last):" in line:
            in_python_traceback = True
            pruned_lines.append(line)
            continue

        if in_python_traceback:
            # Check if this line is an internal framework frame
            if FRAMEWORK_FRAME_PYTHON.search(line) or FRAMEWORK_FRAME_NODE.search(line):
                skipped_framework_frames += 1
                continue
            # End of traceback (Exception line typically starts without indent or with error name)
            if not line.startswith(" ") and not line.startswith("\t") and line.strip():
                in_python_traceback = False
                if skipped_framework_frames > 0:
                    pruned_lines.append(
                        f"  ... [{skipped_framework_frames} interne Framework-/Bibliotheks-Frames ausgelassen] ..."
                    )
                    skipped_framework_frames = 0
                pruned_lines.append(line)
                continue

            if skipped_framework_frames > 0 and (
                line.startswith('  File "') or not line.startswith((" ", "\t"))
            ):
                pruned_lines.append(
                    f"  ... [{skipped_framework_frames} interne Framework-/Bibliotheks-Frames ausgelassen] ..."
                )
                skipped_framework_frames = 0

        pruned_lines.append(line)

    if skipped_framework_frames > 0:
        pruned_lines.append(
            f"  ... [{skipped_framework_frames} interne Framework-/Bibliotheks-Frames ausgelassen] ..."
        )

    result = clean_markdown("```text\n" + "\n".join(pruned_lines) + "\n```")
    return result


def compress_log_file(file_path: Path | str) -> dict[str, Any]:
    """Read a log file and compress it."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Log-Datei nicht gefunden: {path}")

    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    compressed = compress_logs(raw_text)

    orig_tokens = count_tokens(raw_text)
    compressed_tokens = count_tokens(compressed)
    saved = max(0, orig_tokens - compressed_tokens)
    pct = round((saved / orig_tokens * 100.0), 1) if orig_tokens > 0 else 0.0

    return {
        "file_name": path.name,
        "compressed_log": compressed,
        "original_tokens": orig_tokens,
        "reduced_tokens": compressed_tokens,
        "tokens_saved": saved,
        "percentage_saved": pct,
    }
