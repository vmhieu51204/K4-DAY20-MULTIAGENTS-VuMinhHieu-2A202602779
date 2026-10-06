---
name: tabular-data-analysis
description: Use when analyzing sales data, CSV files, or tabular datasets to perform data cleaning, revenue calculations, and generate compliant reports.
---
# Tabular Data Analysis and Reporting Guidelines

1. Python execution rules:
   - Always write data analysis logic into a Python script in workspace (e.g. `workspace/solve.py`) using `write_file`, then run it using `execute` (`python workspace/solve.py`).
   - Do NOT run multi-line or compound statements (`with`, `for`, `if`) using `python -c` in the shell; they cause syntax errors.
   - If execution fails, inspect the error trace and edit the script with `write_file` or `edit_file`. Do not re-run the exact same command.

2. Data processing and cleaning:
   - Use standard library or `pandas`. Handle mixed date formats and timezones properly (e.g. parse to UTC).
   - Filter out missing values (sentinels like `-999`).
   - Deduplicate rows based on record ID.

3. Acme reporting conventions:
   - Money values in `answer.json` must be integer cents (multiply dollar amounts by 100 and convert to integer, e.g. 1606.67 USD is 160667).
   - In `answer.json`, include the required `meta` block:
     `{"source": <input_file_name>, "rows_in": <total rows in input file>, "rows_used": <number of distinct records with known amount>}`.
   - Export cleaned records to `workspace/clean.csv` with header:
     `order_id,timestamp_utc,region,amount_cents`.
   - Format timestamps as ISO-8601 UTC: `YYYY-MM-DDTHH:MM:SSZ`.
   - Standardize region to canonical capitalized spelling (`North`, `South`, `East`, `West`).
   - Express amounts in integer cents.
