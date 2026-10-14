"""Gitignore parsing and pattern matching for codebase traversals."""

import logging
from fnmatch import fnmatch
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_IGNORED_NAMES: set[str] = {
    ".git",
    ".github",
    ".venv",
    "venv",
    ".env",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "Pipfile.lock",
}

DEFAULT_IGNORED_EXTENSIONS: set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".webp",
    ".mp3",
    ".mp4",
    ".wav",
    ".ttf",
    ".woff",
    ".woff2",
}


class GitIgnoreMatcher:
    """Matches relative file paths against .gitignore patterns and default rules."""

    def __init__(self, root_dir: Path, custom_patterns: list[str] | None = None) -> None:
        self.root_dir = root_dir.resolve()
        self.patterns: list[tuple[bool, str]] = []  # (is_negation, pattern)
        self._load_gitignore()
        if custom_patterns:
            for pat in custom_patterns:
                self._add_pattern(pat)

    def _add_pattern(self, line: str) -> None:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return
        is_negation = stripped.startswith("!")
        if is_negation:
            stripped = stripped[1:]
        self.patterns.append((is_negation, stripped))

    def _load_gitignore(self) -> None:
        gitignore_path = self.root_dir / ".gitignore"
        if gitignore_path.is_file():
            try:
                for line in gitignore_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines():
                    self._add_pattern(line)
            except (OSError, UnicodeDecodeError) as exc:
                logger.debug("Could not read .gitignore at %s: %s", gitignore_path, exc)

    def is_ignored(self, path: Path) -> bool:
        """Determine if a file or directory path should be ignored."""
        resolved = path.resolve()
        try:
            rel = resolved.relative_to(self.root_dir)
        except ValueError:
            rel = path

        # Check part-by-part for default ignored names
        for part in rel.parts:
            if part in DEFAULT_IGNORED_NAMES:
                return True

        if resolved.suffix.lower() in DEFAULT_IGNORED_EXTENSIONS:
            return True

        rel_str = rel.as_posix()
        ignored = False

        for is_negation, pat in self.patterns:
            clean_pat = pat.rstrip("/")
            is_dir_pat = pat.endswith("/")
            matched = (
                fnmatch(rel_str, clean_pat)
                or fnmatch(rel.name, clean_pat)
                or (
                    is_dir_pat
                    and (fnmatch(rel_str + "/", pat) or rel_str.startswith(clean_pat + "/"))
                )
                or fnmatch(rel_str, f"*/{clean_pat}")
                or fnmatch(rel_str, f"{clean_pat}/*")
            )

            if matched:
                ignored = not is_negation

        return ignored


def is_path_ignored(path: Path, root_dir: Path) -> bool:
    """Convenience helper to check if a path is ignored against root_dir rules."""
    matcher = GitIgnoreMatcher(root_dir)
    return matcher.is_ignored(path)
