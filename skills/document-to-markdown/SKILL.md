---
name: document-to-markdown
description: >-
  Automatically convert documents (PDF, DOCX, HTML, Jupyter Notebooks) to token-efficient Markdown.
  Use whenever the user provides, attaches, or uploads a document file (e.g. .pdf, .docx, .html, .ipynb),
  asks to read or extract information from a PDF or Word document, or needs to prepare web documentation
  for ingestion without wasting tokens on scripts, styles, navigation bars, or binary image data.
---

# Document to Markdown

## Overview

External specifications, PDFs, manuals, and HTML tutorials frequently contain thousands of tokens of non-informative clutter:

- Binary layout bytes and font metadata in PDFs.
- Navigation menus, headers, footers, JavaScript, and CSS in HTML dumps.
- Verbose chart matrices and terminal outputs in Jupyter Notebooks.

This skill extracts the semantic content (headings, paragraphs, lists, tables, code blocks) and converts it into pure, minimal Markdown.

## When to Use

Activate this skill immediately whenever:

1. The user mentions, attaches, or refers to a `.pdf`, `.docx`, `.html`, or `.ipynb` file.
2. An external specification, PRD, or architecture document must be ingested before planning or implementing.
3. You need to read documentation from a local HTML download without blowing up the context window.

## How to Execute

### Method 1: Using the Bundled Script

Run the executable script via `run_command`:

```bash
uv run python skills/document-to-markdown/scripts/convert_doc.py <PATH_TO_DOC> -o <OUTPUT_MD>
```

Examples:

```bash
# Convert a specification PDF:
uv run python skills/document-to-markdown/scripts/convert_doc.py docs/spec.pdf -o docs/spec.md

# Convert a Jupyter notebook without outputs:
uv run python skills/document-to-markdown/scripts/convert_doc.py notebooks/eda.ipynb -o docs/eda.md
```

### Method 2: In-Memory / Python Import

```python
from src.modules.converter import convert_to_markdown

result = convert_to_markdown("path/to/document.pdf")
markdown_text = result["markdown"]
tokens_saved = result["tokens_saved"]
```

## Verification

- [ ] The generated Markdown contains all functional headings, tables, and code snippets.
- [ ] No base64 image strings (`data:image/...;base64`) or raw HTML boilerplate remain.
- [ ] The Markdown file can be read with `view_file` using significantly fewer tokens (typically 70–95 % savings).
