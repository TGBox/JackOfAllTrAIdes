---
name: codebase-architecture-reporter
description: >-
  Automatically scan a repository directory and generate a compact architecture overview.
  Use whenever analyzing an existing project with an existing folder structure, onboarding to an
  unfamiliar codebase, asked to explain how components interact, or exploring the layout and
  dependencies of a repository before planning or implementing changes.
---

# Codebase Architecture Reporter

## Overview

When an agent enters a new or unfamiliar project, reading every file in the tree destroys the context budget. Most files contain implementation details that are irrelevant to understanding high-level architecture.

This skill scans the project directory, strictly respects `.gitignore` (filtering `.git`, `node_modules`, `.venv`, and lockfiles), and compiles a clean, token-efficient `PROJECT_OVERVIEW.md` detailing:

1. **Kennzahlen & Token-Budget**: Total files, LOC, estimated tokens, and cost.
2. **Top-Token-Verbraucher**: A ranked table of the 10 largest files in the repository.
3. **Erkannte Abhängigkeiten & Module**: Most imported internal modules and third-party packages.
4. **Bereinigter Dateibaum**: Filtered ASCII tree structure.
5. **API-Skelette (optional)**: AST-skeletons of the most critical modules.

## When to Use

Activate this skill immediately whenever:

1. The user asks to explore, summarize, or explain the architecture of an existing project.
2. You begin working in a new repository with an existing folder structure.
3. You need to identify which components exist and how they are wired together before writing a plan or spec.

## How to Execute

### Method 1: Using the Bundled Script

Run the executable script via `run_command`:

```bash
uv run python skills/codebase-architecture-reporter/scripts/generate_report.py [PATH] -o PROJECT_OVERVIEW.md
```

Examples:

```bash
# Scan current workspace and save report:
uv run python skills/codebase-architecture-reporter/scripts/generate_report.py . -o PROJECT_OVERVIEW.md

# Scan with API skeletons of key components included:
uv run python skills/codebase-architecture-reporter/scripts/generate_report.py . --skeletons --max-skeletons 5 -o PROJECT_OVERVIEW.md
```

### Method 2: In-Memory / Python Import

```python
from src.modules.reporter import generate_project_report

report_data = generate_project_report(".", include_skeletons=True)
markdown_summary = report_data["markdown"]
top_files = report_data["top_consumers"]
```

## Verification

- [ ] `.git`, `.venv`, `node_modules` and lockfiles are completely excluded from the report.
- [ ] The generated report clearly identifies the core components and external libraries.
- [ ] Reading `PROJECT_OVERVIEW.md` requires less than 5 % of the tokens needed to inspect the full codebase.
