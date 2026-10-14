"""Data and Schema Reducer: Compresses JSON, CSV, and SQL dumps into schemas with minimal sample rows."""

import csv
import io
import json
import re
from pathlib import Path
from typing import Any

from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens

SQL_INSERT_REGEX = re.compile(
    r"(INSERT\s+INTO\s+[`\"']?[a-zA-Z0-9_]+[`\"']?\s*(?:\([^)]+\))?\s*VALUES\s*)([\s\S]*?;)",
    re.IGNORECASE,
)


def _infer_type(val: Any) -> str:
    """Infer high-level JSON/Python type name."""
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "boolean"
    if isinstance(val, int):
        return "integer"
    if isinstance(val, float):
        return "float"
    if isinstance(val, list):
        elem_type = _infer_type(val[0]) if val else "any"
        return f"array[{elem_type}]"
    if isinstance(val, dict):
        return "object"
    return "string"


def reduce_json(raw_json: str, max_samples: int = 2) -> str:
    """Reduce large JSON payloads by trimming repetitive arrays and showing schemas."""
    data = json.loads(raw_json)

    def _truncate_recursive(node: Any) -> Any:
        if isinstance(node, list):
            total_items = len(node)
            if total_items > max_samples:
                sampled = [_truncate_recursive(item) for item in node[:max_samples]]
                sampled.append(
                    f"... [und {total_items - max_samples} weitere Elemente ausgelassen]"
                )
                return sampled
            return [_truncate_recursive(item) for item in node]
        if isinstance(node, dict):
            return {k: _truncate_recursive(v) for k, v in node.items()}
        return node

    schema_info: list[str] = []
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Extract schema table for root list of objects
        first_item = data[0]
        schema_info.append("### Erkanntes Schema:")
        schema_info.append("| Feld | Typ | Beispiel |")
        schema_info.append("|---|---|---|")
        for k, v in first_item.items():
            schema_info.append(f"| `{k}` | `{_infer_type(v)}` | `{str(v)[:40]}` |")
        schema_info.append(
            f"\n*Gesamtanzahl Objekte: {len(data)} (auf {max_samples} Beispieldatenzeilen gekürzt)*"
        )

    reduced_obj = _truncate_recursive(data)
    formatted_json = json.dumps(reduced_obj, indent=2, ensure_ascii=False)

    parts: list[str] = []
    if schema_info:
        parts.append("\n".join(schema_info))
    parts.append(f"```json\n{formatted_json}\n```")

    return clean_markdown("\n\n".join(parts))


def reduce_csv(raw_csv: str, max_rows: int = 3) -> str:
    """Extract column headers, infer types, and output minimal sample table."""
    reader = csv.reader(io.StringIO(raw_csv.strip()))
    rows = list(reader)
    if not rows:
        return "*Leere CSV-Daten.*"

    headers = rows[0]
    data_rows = rows[1:]
    total_data_rows = len(data_rows)

    type_guesses: list[str] = []
    if data_rows:
        sample_row = data_rows[0]
        for val in sample_row:
            val_clean = val.strip()
            if val_clean.isdigit():
                type_guesses.append("int")
            elif re.match(r"^-?\d+\.\d+$", val_clean):
                type_guesses.append("float")
            elif val_clean.lower() in ("true", "false"):
                type_guesses.append("bool")
            else:
                type_guesses.append("str")
    else:
        type_guesses = ["str"] * len(headers)

    md_lines: list[str] = [
        "### CSV-Schema & Beispieldaten",
        f"*Gesamtzeilen im Original: {total_data_rows:,} | Angezeigt: {min(max_rows, total_data_rows)}*",
        "",
        "| "
        + " | ".join([f"**{h}** ({t})" for h, t in zip(headers, type_guesses, strict=False)])
        + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in data_rows[:max_rows]:
        padded = row + [""] * (len(headers) - len(row))
        md_lines.append("| " + " | ".join(padded[: len(headers)]) + " |")

    if total_data_rows > max_rows:
        md_lines.append(
            f"\n*... und {total_data_rows - max_rows:,} weitere Datenzeilen für Token-Ersparnis ausgelassen.*"
        )

    return clean_markdown("\n".join(md_lines))


def reduce_sql(raw_sql: str, max_inserts: int = 2) -> str:
    """Retain DDL schemas while pruning large bulk INSERT statements."""
    lines = raw_sql.splitlines()
    pruned_lines: list[str] = []
    insert_block_count = 0
    in_insert = False

    for line in lines:
        stripped = line.strip()
        if stripped.upper().startswith("INSERT INTO"):
            insert_block_count += 1
            if insert_block_count <= max_inserts:
                pruned_lines.append(line)
            elif insert_block_count == max_inserts + 1:
                pruned_lines.append(
                    "-- [Weitere INSERT-Statements ausgelassen, um Tokens zu sparen...]"
                )
            in_insert = not stripped.endswith(";")
            continue

        if in_insert:
            if stripped.endswith(";"):
                in_insert = False
            continue

        pruned_lines.append(line)

    result_sql = "\n".join(pruned_lines)
    return clean_markdown(f"```sql\n{result_sql}\n```")


def reduce_data_file(file_path: Path | str, max_samples: int = 3) -> dict[str, Any]:
    """Unified file-based entry point for data schema reduction."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")

    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    ext = path.suffix.lower()

    if ext == ".json":
        reduced = reduce_json(raw_text, max_samples=max_samples)
    elif ext in (".csv", ".tsv"):
        reduced = reduce_csv(raw_text, max_rows=max_samples)
    elif ext == ".sql":
        reduced = reduce_sql(raw_text, max_inserts=max_samples)
    else:
        reduced = raw_text

    orig_tokens = count_tokens(raw_text)
    reduced_tokens = count_tokens(reduced)
    saved = max(0, orig_tokens - reduced_tokens)
    pct = round((saved / orig_tokens * 100.0), 1) if orig_tokens > 0 else 0.0

    return {
        "file_name": path.name,
        "format": ext,
        "reduced_markdown": reduced,
        "original_tokens": orig_tokens,
        "reduced_tokens": reduced_tokens,
        "tokens_saved": saved,
        "percentage_saved": pct,
    }
