---
name: python-code-skeletonizer
description: >-
  Extract structural Python interfaces by stripping function and method bodies via Python AST.
  Use whenever referencing large existing Python modules as context, inspecting API contracts or
  data models, or when the agent needs to call existing services without reading thousands of lines
  of implementation details.
---

# Python Code Skeletonizer

## Overview

When writing code that interacts with existing project modules (e.g. database layers, external API clients, large utility classes), reading hundreds of lines of algorithmic implementations wastes precious context.

The Python AST Code Skeletonizer parses the source code using `ast`, replaces the body of every function and method with `...` (Ellipsis), and preserves:

- Class definitions and inheritance hierarchies.
- Function and method signatures (`def foo(x: int) -> str:`).
- Type annotations and default arguments.
- Decorators (`@property`, `@staticmethod`, etc.).
- Complete docstrings explaining what each method does.

## When to Use

Activate this skill immediately whenever:

1. You need to understand how to call or interact with an existing class or module.
2. A Python file exceeds 200 lines and is only being read as a dependency or reference.
3. You need to provide the agent with a clean API interface without blowing up token usage.

## How to Execute

### Method 1: Using the Bundled Script

Run the executable script via `run_command`:

```bash
uv run python skills/python-code-skeletonizer/scripts/skeletonize.py <PATH_TO_PY_FILE> [-o <OUTPUT_PATH>]
```

Examples:

```bash
# Skeletonize a database service and print to stdout:
uv run python skills/python-code-skeletonizer/scripts/skeletonize.py src/database/client.py

# Save skeleton interface file:
uv run python skills/python-code-skeletonizer/scripts/skeletonize.py src/api/router.py -o docs/api_interface.py
```

### Method 2: In-Memory / Python Import

```python
from src.modules.skeletonizer import skeletonize_code

with open("src/services/heavy.py") as f:
    skeleton = skeletonize_code(f.read(), keep_docstrings=True)
```

## Verification

- [ ] Output is syntactically valid Python code.
- [ ] All function bodies are replaced with `...`.
- [ ] Method names, parameters, return types, and docstrings are intact.
- [ ] Token savings are typically between 60 % and 85 %.
