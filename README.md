# AZ Copilot Backend Lab (October 2026)

Repository for the workshop "GitHub Copilot for Backend Development", hands-on lab "From Ticket to Pull Request".
It is a small sandbox (internal name: dwh-pulse) that imitates the daily work of a sales data warehouse team with customers, products and orders. All data, names and tickets are synthetic.

```text
src (simulated Oracle) -> stg -> core -> mart -> Power BI model (powerbi/model.md)
        Python orchestration: pipeline.py, runner.py, one log row per step in ctl.dwh_control
```

## Purpose
Practice the loop ticket, explore, plan, implement, verify, review and pull request on code that looks like a DWH backend: SQL transformations, a Python runner and a status report.

Oracle is simulated with SQLite: each schema (src, stg, core, mart, ctl) is its own database file in `data/`. The SQL is written Oracle-style, with small dialect differences marked in comments.

## Local setup
```bash
uv sync                # installs pydantic and pytest
uv run dwh seed        # simulated source data and a demo run history
uv run dwh status      # the status report you improve in Part 1 of the lab
uv run dwh run         # run the pipeline for real
uv run dwh peek mart.fact_orders   # look at the first rows of any table
uv run scripts/render_report.py    # Power BI report preview (simulation) -> exports/report.html
uv run pytest
```

### No uv on your machine?
Use the dev container: install Docker and the VS Code extension "Dev Containers", open the repo folder and run "Dev Containers: Reopen in Container". `.devcontainer/` installs Python 3.13, uv and the Copilot extensions, then runs `uv sync` and `uv run dwh seed`. All commands in the lab work unchanged in its terminal.

## Structure
| Path | Content |
|---|---|
| `sql/` | all transformations, numbered per layer |
| `src/dwhpulse/` | pipeline definition, runner, status report, seed data, CLI |
| `powerbi/` | documentation of the Power BI model (tables, relationships, DAX, lineage) |
| `docs/confluence/` | simulated process pages |
| `tickets/` | simulated Jira tickets DWH-101 to DWH-103 |
| `scripts/` | `lab_check.py` (finish line for DWH-101), `export_powerbi.py`, `render_report.py` (HTML preview of the Power BI report, a simulation) |
| `tests/` | unit tests and repository conventions |
| `solutions/` | reference solutions for DWH-101 and DWH-103, look only after you tried |
| `.agents/` | agent skills and their provenance |

## Conventions
- Transformations only in SQL files, never in Python. No `SELECT *`. SRC is read only.
- Every pipeline step logs into `ctl.dwh_control`. A failed step skips what depends on it.
- Behavior change -> test first. Fixtures stay synthetic.
- README and AGENTS.md follow structural changes.
