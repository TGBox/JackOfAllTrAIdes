"""Document to token-efficient Markdown converter supporting PDF, DOCX, HTML, and IPYNB."""

import json
from pathlib import Path
from typing import Any

import docx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from src.core.text_utils import clean_markdown
from src.core.tokenizer import count_tokens


def convert_pdf_to_markdown(file_path: Path | str) -> str:
    """Extract and format text from PDF into clean Markdown without binary clutter."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF-Datei nicht gefunden: {path}")

    reader = PdfReader(str(path))
    pages_md: list[str] = []

    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text_clean = text.strip()
        if text_clean:
            pages_md.append(f"## Seite {idx}\n\n{text_clean}")

    combined = "\n\n---\n\n".join(pages_md)
    return clean_markdown(combined)


def convert_docx_to_markdown(file_path: Path | str) -> str:
    """Extract headings, paragraphs, and tables from DOCX into structured Markdown."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"DOCX-Datei nicht gefunden: {path}")

    doc = docx.Document(str(path))
    md_blocks: list[str] = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name.lower() if para.style else ""
        if "heading 1" in style_name:
            md_blocks.append(f"# {text}")
        elif "heading 2" in style_name:
            md_blocks.append(f"## {text}")
        elif "heading 3" in style_name:
            md_blocks.append(f"### {text}")
        elif "list" in style_name or "bullet" in style_name:
            md_blocks.append(f"- {text}")
        else:
            md_blocks.append(text)

    for table in doc.tables:
        rows: list[list[str]] = []
        for row in table.rows:
            cell_texts = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            rows.append(cell_texts)

        if not rows:
            continue

        # Header row
        header = "| " + " | ".join(rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * len(rows[0])) + " |"
        table_lines = [header, separator]

        for data_row in rows[1:]:
            table_lines.append("| " + " | ".join(data_row) + " |")

        md_blocks.append("\n".join(table_lines))

    return clean_markdown("\n\n".join(md_blocks))


def convert_html_to_markdown(html_content_or_path: Path | str) -> str:
    """Strip boilerplate (scripts, styles, navs, footers) and convert HTML to concise Markdown."""
    raw_html: str
    if isinstance(html_content_or_path, Path) or (
        isinstance(html_content_or_path, str) and Path(html_content_or_path).is_file()
    ):
        raw_html = Path(html_content_or_path).read_text(encoding="utf-8", errors="ignore")
    else:
        raw_html = str(html_content_or_path)

    soup = BeautifulSoup(raw_html, "html.parser")

    # Strip noisy elements
    for tag in soup(
        [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "noscript",
            "svg",
            "button",
            "iframe",
        ]
    ):
        tag.decompose()

    md_blocks: list[str] = []

    # Process headings
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "ul", "ol", "table"]):
        name = tag.name
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        if name == "h1":
            md_blocks.append(f"# {text}")
        elif name == "h2":
            md_blocks.append(f"## {text}")
        elif name == "h3":
            md_blocks.append(f"### {text}")
        elif name in ("h4", "h5", "h6"):
            md_blocks.append(f"#### {text}")
        elif name == "p":
            md_blocks.append(text)
        elif name == "pre":
            md_blocks.append(f"```\n{tag.get_text(strip=False)}\n```")
        elif name in ("ul", "ol"):
            items = [
                f"- {li.get_text(strip=True)}"
                for li in tag.find_all("li")
                if li.get_text(strip=True)
            ]
            if items:
                md_blocks.append("\n".join(items))
        elif name == "table":
            table_rows: list[list[str]] = []
            for tr in tag.find_all("tr"):
                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
                if cells:
                    table_rows.append(cells)
            if table_rows:
                header = "| " + " | ".join(table_rows[0]) + " |"
                sep = "| " + " | ".join(["---"] * len(table_rows[0])) + " |"
                lines = [header, sep]
                for r in table_rows[1:]:
                    lines.append("| " + " | ".join(r) + " |")
                md_blocks.append("\n".join(lines))

    # Fallback to general text if no semantic tags found
    if not md_blocks:
        fallback_text = soup.get_text("\n", strip=True)
        return clean_markdown(fallback_text)

    return clean_markdown("\n\n".join(md_blocks))


def convert_ipynb_to_markdown(file_path: Path | str, include_outputs: bool = False) -> str:
    """Convert Jupyter Notebook cells into Markdown, skipping verbose outputs to save tokens."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Notebook-Datei nicht gefunden: {path}")

    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    cells = data.get("cells", [])

    md_blocks: list[str] = [f"# Jupyter Notebook: {path.name}"]

    for idx, cell in enumerate(cells, start=1):
        cell_type = cell.get("cell_type", "")
        source_lines = cell.get("source", [])
        source_text = "".join(source_lines).strip()

        if not source_text:
            continue

        if cell_type == "markdown":
            md_blocks.append(source_text)
        elif cell_type == "code":
            block = f"```python\n# [Zelle {idx}]\n{source_text}\n```"
            if include_outputs:
                outputs = cell.get("outputs", [])
                text_outputs: list[str] = []
                for out in outputs:
                    if "text" in out:
                        text_outputs.append("".join(out["text"]).strip())
                    elif "data" in out and "text/plain" in out["data"]:
                        text_outputs.append("".join(out["data"]["text/plain"]).strip())
                if text_outputs:
                    joined_outputs = "\n".join(text_outputs)
                    block += f"\n\n*Output:*\n```\n{truncate_outputs(joined_outputs)}\n```"
            md_blocks.append(block)

    return clean_markdown("\n\n".join(md_blocks))


def truncate_outputs(output_text: str, max_lines: int = 15) -> str:
    """Truncate long terminal or execution outputs in notebooks."""
    lines = output_text.splitlines()
    if len(lines) <= max_lines:
        return output_text
    return "\n".join(lines[:max_lines]) + "\n... [Restliche Output-Zeilen ausgelassen]"


def convert_to_markdown(file_path: Path | str, include_outputs: bool = False) -> dict[str, Any]:
    """Unified entrypoint detecting file extension and converting to Markdown with token stats.

    Returns:
        dict containing 'markdown', 'original_tokens', 'reduced_tokens', 'tokens_saved'
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        markdown = convert_pdf_to_markdown(path)
    elif ext in (".docx", ".doc"):
        markdown = convert_docx_to_markdown(path)
    elif ext in (".html", ".htm"):
        markdown = convert_html_to_markdown(path)
    elif ext == ".ipynb":
        markdown = convert_ipynb_to_markdown(path, include_outputs=include_outputs)
    else:
        # Default text read
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        markdown = clean_markdown(raw_text)

    # Estimate original tokens (binary or full text)
    try:
        raw_size = path.stat().st_size
        estimated_raw_tokens = max(1, int(raw_size / 3.8))
    except (OSError, ValueError):
        estimated_raw_tokens = count_tokens(markdown)

    reduced_tokens = count_tokens(markdown)

    return {
        "file_name": path.name,
        "format": ext,
        "markdown": markdown,
        "estimated_raw_tokens": estimated_raw_tokens,
        "reduced_tokens": reduced_tokens,
        "tokens_saved": max(0, estimated_raw_tokens - reduced_tokens),
    }
