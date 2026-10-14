"""Token estimation using tiktoken with robust heuristic fallback."""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Common models and approximate input costs per 1,000,000 tokens (in USD)
MODEL_PRICING: dict[str, float] = {
    "claude-3-5-sonnet": 3.00,
    "gpt-4o": 2.50,
    "gpt-4o-mini": 0.15,
    "gemini-1-5-pro": 3.50,
    "gemini-1-5-flash": 0.075,
}


@lru_cache(maxsize=4)
def _get_tiktoken_encoding(encoding_name: str = "cl100k_base"):
    """Cache tiktoken encoding to avoid repeated initialization."""
    try:
        import tiktoken

        return tiktoken.get_encoding(encoding_name)
    except (ImportError, ValueError, KeyError) as exc:
        logger.debug("Failed to load tiktoken encoding '%s': %s", encoding_name, exc)
        return None


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken, falling back to a 4-char heuristic.

    Args:
        text: The string content to measure.
        encoding_name: tiktoken encoding identifier (e.g. 'cl100k_base' or 'o200k_base').

    Returns:
        Estimated or exact number of tokens.
    """
    if not text:
        return 0

    encoding = _get_tiktoken_encoding(encoding_name)
    if encoding is not None:
        try:
            return len(encoding.encode(text, disallowed_special=()))
        except (ValueError, TypeError) as exc:
            logger.debug("Encoding error during token calculation: %s", exc)

    # Heuristic fallback: roughly 1 token per 3.7 - 4 characters for code/text
    return max(1, int(len(text) / 3.8))


def estimate_token_cost(token_count: int, model_name: str = "claude-3-5-sonnet") -> float:
    """Calculate the estimated input cost in USD for the given token count."""
    price_per_million = MODEL_PRICING.get(model_name.lower(), 3.00)
    return (token_count / 1_000_000.0) * price_per_million
