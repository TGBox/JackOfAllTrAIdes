"""Text normalization, Markdown cleanup, and formatting utilities."""

import re
from typing import Any

# Regex to detect base64 data URIs commonly inlined in HTML/Markdown
BASE64_DATA_REGEX = re.compile(r"data:image\/[a-zA-Z0-9.+_-]+;base64,[A-Za-z0-9+/=]{40,}")

# HTML comments like <!-- ... -->
HTML_COMMENT_REGEX = re.compile(r"<!--[\s\S]*?-->")

# Excessive newlines (> 2 consecutive blank lines)
EXCESSIVE_NEWLINES_REGEX = re.compile(r"\n{3,}")


def clean_markdown(text: str, strip_comments: bool = True, strip_base64: bool = True) -> str:
    """Purify markdown content by stripping redundant whitespace and heavy binary payloads.

    Args:
        text: Raw markdown text.
        strip_comments: Remove HTML comment markers.
        strip_base64: Replace massive base64 image data URIs with short placeholders.

    Returns:
        Cleaned, token-efficient markdown string.
    """
    if not text:
        return ""

    result = text

    if strip_base64:
        result = BASE64_DATA_REGEX.sub("[Bild: Base64-Daten entfernt]", result)

    if strip_comments:
        result = HTML_COMMENT_REGEX.sub("", result)

    # Normalize carriage returns and trailing whitespace on lines
    lines = [line.rstrip() for line in result.splitlines()]
    result = "\n".join(lines)

    # Collapse more than 2 consecutive newlines into 2
    result = EXCESSIVE_NEWLINES_REGEX.sub("\n\n", result)

    return result.strip() + "\n"


def truncate_text(text: str, max_chars: int = 10000, suffix: str = "\n... [Gekürzt]") -> str:
    """Safely truncate text if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + suffix


def format_token_savings(original_tokens: int, reduced_tokens: int) -> dict[str, Any]:
    """Calculate and format token reduction statistics."""
    saved = max(0, original_tokens - reduced_tokens)
    pct = (saved / original_tokens * 100.0) if original_tokens > 0 else 0.0
    return {
        "original_tokens": original_tokens,
        "reduced_tokens": reduced_tokens,
        "tokens_saved": saved,
        "percentage_saved": round(pct, 1),
    }
