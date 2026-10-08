# Pipeline operations (simulated Confluence page)

## Layers
- SRC: simulated source system. Read only.
- STG: raw copy plus load timestamp. No business logic.
- CORE: cleaned and conformed data. Credit-blocked customers and discontinued products stop here.
- MART: tables for reporting, one per Power BI table.

## Run and status
- The pipeline starts at 05:00. Every step writes one row into ctl.dwh_control.
- A step that fails is logged as FAILED with the Oracle error. Steps that depend on it are SKIPPED.
- The status must be readable for people who are not data engineers, and available by 06:00.
- A successful step that finishes after 06:00:00 counts as late. A step that finishes at exactly 06:00:00 is on time.
- Lateness is reported in started minutes: a step that finishes at 06:00:30 is 1 min late.
- Failed and skipped steps are reported as FAILED or SKIPPED, never as late.

## Naming
- Step names: layer prefix plus table, for example `core_orders`.
- SQL files are numbered per layer and run in the order of pipeline.py.
- No SELECT * in SQL files. Explicit column lists only.

## Errors
- Bad source rows (duplicates, amounts of 0 or less, unknown customers) are reported before the Monday review.
- A rerun of any step must give the same result (idempotent).
