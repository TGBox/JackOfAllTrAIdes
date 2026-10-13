---
name: git-diff-packager
description: >-
  Package git working tree or staged diffs together with AST interface skeletons of all modified files.
  Use whenever preparing pull requests, conducting code reviews, reviewing uncommitted changes,
  or analyzing recent edits without reading the entire repository.
---

# Git Diff Context Packager

## Overview

Code review agents or subagents tasked with auditing a diff often lack context regarding the surrounding class, methods, or type definitions in the changed files. Providing full file contents wastes tokens; providing only raw `git diff` chunks often omits critical class definitions and signatures.

The Git Diff Context Packager resolves this by:

1. Extracting the active `git diff` (working tree or `--staged`).
2. Detecting every modified file.
3. Automatically generating AST skeletons (interfaces, docstrings, signatures) for modified Python files.
4. Packaging both into a clean, markdown-formatted code review package.

## When to Use

Activate this skill immediately whenever:

1. The user asks for a code review or summary of their uncommitted changes.
2. You or a subagent need to review recent edits before staging or finishing a task.
3. You need to produce an audit or review artifact without loading all modified files in full.

## How to Execute

### Method 1: Using the Bundled Script

Run via `run_command`:

```bash
uv run python skills/git-diff-packager/scripts/pack_diff.py [-r <REPO_PATH>] [--staged] [--no-skeletons] [-o <OUTPUT_PATH>]
```

Examples:

```bash
# Package working tree diff with file skeletons and print to stdout:
uv run python skills/git-diff-packager/scripts/pack_diff.py

# Package staged changes into a review markdown file:
uv run python skills/git-diff-packager/scripts/pack_diff.py --staged -o context/review_package.md
```

### Method 2: In-Memory / Python Import

```python
from src.modules.diff_packager import package_git_diff

review_pkg = package_git_diff(".", staged=False, include_skeletons=True)
print(review_pkg["packaged_markdown"])
```

## Verification

- [ ] Changed file list is accurate.
- [ ] Diff syntax block is properly closed and readable.
- [ ] Interface skeletons provide method signatures and docstrings of modified files.
