---
name: token-usage-router
description: >-
  Meta-router for token reduction and context compression.
  Use whenever the user provides or uploads documents (PDF, DOCX, HTML, IPYNB),
  asks to explore, onboard, or analyze an unfamiliar or new project directory,
  shares large data payloads (JSON, CSV, SQL dumps), pastes verbose logs/tracebacks,
  or asks to prepare and optimize context for coding agents without overflowing the context window.
---

# Token Usage Router

## Overview

Working with AI coding agents requires strict context budgeting. Blindly dumping entire repositories, raw PDFs, huge JSON test fixtures, or 500-line stack traces wastes tens of thousands of tokens, increases latency, and causes the LLM to hallucinate or miss critical instructions.

This router directs you to the exact specialized token reduction skill to use based on the input:

```text
Input / Scenario
    │
    ├── Uploaded/provided document (PDF, DOCX, HTML, .ipynb) ────→ document-to-markdown
    │
    ├── New/unfamiliar project directory to explore/onboard ──────→ codebase-architecture-reporter
    │
    ├── Large Python file to use as API contract / interface ──→ python-code-skeletonizer
    │
    ├── Bulky data payload (JSON, CSV, SQL dump) ───────────────→ data-schema-reducer
    │
    ├── Terminal errors, verbose logs, framework tracebacks ────→ log-stacktrace-compressor
    │
    ├── Feature slice around a specific entry file ─────────────→ dependency-context-collector
    │
    └── Reviewing / testing recent git changes ─────────────────→ git-diff-packager
```

## Routing Matrix

| Signal / Trigger | Ziel-Skill | Erwartete Ersparnis |
| --- | --- | --- |
| Der Nutzer lädt eine PDF, ein Word-Dokument (`.docx`), eine HTML-Seite oder ein Jupyter Notebook (`.ipynb`) hoch | `document-to-markdown` | **70 % – 95 %** |
| Ein neues Projekt oder ein vorhandener Ordner soll analysiert, zusammengefasst oder erkundet werden | `codebase-architecture-reporter` | **90 % – 99 %** |
| Eine bestehende Python-Klasse oder ein Modul soll als Kontext dienen, ohne dass der Rumpf geändert werden muss | `python-code-skeletonizer` | **60 % – 85 %** |
| Ein Daten-Dump, API-Payload oder Fixture (JSON, CSV, SQL) soll dem Agenten gezeigt werden | `data-schema-reducer` | **90 % – 99 %** |
| Ein Fehlerbericht, Terminal-Dump oder Stacktrace soll untersucht werden | `log-stacktrace-compressor` | **75 % – 90 %** |
| Ein Feature soll implementiert werden, das auf einem Teilbaum lokaler Imports basiert | `dependency-context-collector` | **80 % – 95 %** |
| Der Agent soll aktuelle Änderungen reviewen, testen oder eine PR-Beschreibung verfassen | `git-diff-packager` | **70 % – 90 %** |

## Best Practices

1. **Immer vor dem Prompten reduzieren**: Reduziere Dokumente und Datenbestände *bevor* du sie in den Agenten-Kontext ziehst.
2. **Dateipfade statt Volltext**: Wenn eine Datei im Workspace existiert, führe das entsprechende Reduktions-Skript aus und lies nur die komprimierte Ausgabe.
3. **Kombinieren erlaubt**: Bei großen Projekten kombiniert man oft den `codebase-architecture-reporter` mit `python-code-skeletonizer` für die 3–4 Kern-Module.
