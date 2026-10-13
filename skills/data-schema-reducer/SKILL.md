---
name: data-schema-reducer
description: >-
  Compress bulky JSON payloads, CSV datasets, and SQL dumps into schemas with minimal sample rows.
  Use whenever the user provides, uploads, or references large data fixtures, database dumps, or API
  responses, or asks to write queries, models, or data parsers without filling the context window with
  thousands of repetitive data records.
---

# Data & Schema Reducer

## Overview

Coding agents do not need 10,000 records of real customer data to write a database query, data transformation, or Pydantic model. They only need:

1. The field/column names.
2. The inferred data types (integer, float, string, boolean, array, object).
3. 2–3 representative sample rows to understand formatting conventions (e.g., date formats or ID prefixes).

This skill reduces massive JSON arrays, CSV spreadsheets, and SQL dumps by 90 % to 99 % while retaining full structural fidelity.

## When to Use

Activate this skill immediately whenever:

1. The user references a `.json`, `.csv`, `.tsv`, or `.sql` file that contains repetitive data.
2. An API endpoint response or database table structure needs to be examined.
3. You are designing schemas, migrations, or data pipelines based on sample inputs.

## How to Execute

### Method 1: Using the Bundled Script

Run the executable script via `run_command`:

```bash
uv run python skills/data-schema-reducer/scripts/reduce_data.py <PATH_TO_DATA_FILE> [-s <SAMPLES>] [-o <OUTPUT_PATH>]
```

Examples:

```bash
# Reduce a large JSON fixture to schema + 2 sample records:
uv run python skills/data-schema-reducer/scripts/reduce_data.py tests/fixtures/users.json -s 2

# Extract schema from a CSV file:
uv run python skills/data-schema-reducer/scripts/reduce_data.py data/transactions.csv -o docs/transactions_schema.md

# Prune bulk INSERT statements from a SQL dump:
uv run python skills/data-schema-reducer/scripts/reduce_data.py db/backup.sql -o db/schema_only.sql
```

### Method 2: In-Memory / Python Import

```python
from src.modules.data_reducer import reduce_json, reduce_csv, reduce_sql

# For JSON:
compact_md = reduce_json(raw_json_string, max_samples=2)

# For CSV:
table_md = reduce_csv(raw_csv_string, max_rows=3)
```

## Verification

- [ ] Schema table lists all keys/columns with correct data types.
- [ ] Only 2–3 sample records are retained; remaining bulk records are replaced with a concise truncation notice.
- [ ] Token savings typically exceed 90 %.
