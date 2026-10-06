---
name: acme-log-triage
description: Use when parsing application logs or triaging error logs to comply with log analysis and Acme conventions.
---
# Acme Log Triage Conventions

1. Execution safety:
   - Write parsing scripts to a file (e.g. `workspace/parse_logs.py`) using `write_file` and run with `execute` (`python workspace/parse_logs.py`).
   - Avoid inline one-liners with `python -c` that contain compound statements.

2. Acme triage formatting:
   - Normalize service names: convert to lowercase and replace hyphens `-` with underscores `_` (e.g. `payment-service` becomes `payment_service`) in both error objects and `counts_by_service` keys.
   - Sort the list of errors chronologically by `timestamp_utc` ascending.
   - Timestamps must be ISO-8601 UTC formatted: `YYYY-MM-DDTHH:MM:SSZ`.
   - `exception`: extract the last line of the exception traceback if present, otherwise set to null.
   - `repeat_count`: 1 + sum of all repeated line counts following the entry.
