"""Python AST Skeletonizer: Strips function and method bodies, keeping signatures and docstrings."""

import ast
from pathlib import Path
from typing import Any

from src.core.tokenizer import count_tokens


class CodeSkeletonTransformer(ast.NodeTransformer):
    """AST transformer that replaces function/method implementations with Ellipsis (...) while preserving docstrings."""

    def __init__(self, keep_docstrings: bool = True) -> None:
        self.keep_docstrings = keep_docstrings

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._transform_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        return self._transform_function(node)

    def _transform_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        docstring = ast.get_docstring(node) if self.keep_docstrings else None

        new_body: list[ast.stmt] = []
        if docstring:
            new_body.append(ast.Expr(value=ast.Constant(value=docstring)))

        # Add Ellipsis (...) as the body stub
        new_body.append(ast.Expr(value=ast.Constant(value=...)))

        node.body = new_body
        return node


def skeletonize_code(source_code: str, keep_docstrings: bool = True) -> str:
    """Transform Python source code into a compact interface skeleton.

    Args:
        source_code: Raw Python code.
        keep_docstrings: Whether to retain docstrings for contextual meaning.

    Returns:
        Stripped Python code with functions replaced by '...'.
    """
    if not source_code.strip():
        return ""

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        return f"# [Syntax-Fehler beim Parsen: {exc.msg} (Zeile {exc.lineno})]\n{source_code}"

    transformer = CodeSkeletonTransformer(keep_docstrings=keep_docstrings)
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    try:
        return ast.unparse(transformed_tree)
    except (ValueError, TypeError) as exc:
        return f"# [Fehler bei der AST-Code-Generierung: {exc}]\n{source_code}"


def skeletonize_file(file_path: Path | str, keep_docstrings: bool = True) -> dict[str, Any]:
    """Read a Python file, skeletonize it, and calculate token savings.

    Returns:
        dict with keys: 'file_name', 'skeleton', 'original_tokens', 'reduced_tokens', 'percentage_saved'
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Python-Datei nicht gefunden: {path}")

    raw_code = path.read_text(encoding="utf-8", errors="ignore")
    skeleton = skeletonize_code(raw_code, keep_docstrings=keep_docstrings)

    orig_tokens = count_tokens(raw_code)
    skeleton_tokens = count_tokens(skeleton)
    saved = max(0, orig_tokens - skeleton_tokens)
    pct = round((saved / orig_tokens * 100.0), 1) if orig_tokens > 0 else 0.0

    return {
        "file_name": path.name,
        "skeleton": skeleton,
        "original_tokens": orig_tokens,
        "reduced_tokens": skeleton_tokens,
        "tokens_saved": saved,
        "percentage_saved": pct,
    }
