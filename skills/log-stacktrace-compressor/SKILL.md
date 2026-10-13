---
name: log-stacktrace-compressor
description: >-
  Sanitize and compress terminal outputs, CI/CD run logs, pytest failures, and long stack traces.
  Deduplicates repeating log lines, strips ANSI escape sequences, collapses internal runtime traceback
  frames, and extracts the core root cause. Use whenever diagnosing test failures, analyzing server
  logs, or processing large command outputs.
---

# Log & Stacktrace Compressor

## Overview

Terminal outputs, test execution logs (e.g. `pytest`, `npm test`), and web server crash dumps frequently contain hundreds of lines of repetitive noise:

- ANSI color codes and escape sequences.
- Repetitive heartbeat, polling, or debug messages.
- Dozens of internal framework frames (e.g. `site-packages`, standard library internals) that obscure the real application failure point.

The Log & Stacktrace Compressor sanitizes this noise, deduplicates repeating sequences (e.g. `... [Repeated 45 times]`), prunes irrelevant internal frames, and highlights the exact root cause exception and line number.

## When to Use

Activate this skill immediately whenever:

1. A test suite or command execution produces a large error output or stack trace.
2. The user pastes a raw server log, exception dump, or terminal output.
3. You need to diagnose a runtime error without loading thousands of irrelevant logging lines into the conversation context.

## How to Execute

### Method 1: Using the Bundled Script

Run via `run_command` on a log file or piped input:

```bash
uv run python skills/log-stacktrace-compressor/scripts/compress_log.py <PATH_TO_LOG_FILE> [-o <OUTPUT_PATH>]
```

Examples:

```bash
# Compress a crash log and print to stdout:
uv run python skills/log-stacktrace-compressor/scripts/compress_log.py tests/failure.log

# Pipe a failing test run directly through the compressor:
uv run pytest | uv run python skills/log-stacktrace-compressor/scripts/compress_log.py

# Save the compressed output:
uv run python skills/log-stacktrace-compressor/scripts/compress_log.py logs/server.log -o logs/server_clean.log
```

### Method 2: In-Memory / Python Import

```python
from src.modules.log_compressor import compress_logs

raw_error = run_failing_command()
clean_error = compress_logs(raw_error)
```

## Verification

- [ ] ANSI escape characters are completely removed.
- [ ] The underlying Exception name, message, and application source lines are clearly visible.
- [ ] Repeating lines are condensed with a count indicator.
