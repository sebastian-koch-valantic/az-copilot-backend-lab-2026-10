# Project instructions

Small sandbox pipeline: simulated Oracle source -> SQL layers (STG, CORE, MART) -> Python
orchestration -> Power BI model documentation. All data is synthetic.

## Commands
- Set up the data: `uv run dwh seed`
- Run the pipeline: `uv run dwh run` (add `--inject-failure core_orders` to simulate an Oracle error)
- Show the status: `uv run dwh status`
- Look at a table: `uv run dwh peek mart.fact_orders`
- Run the tests: `uv run pytest`
- Preview the Power BI report (simulation): `uv run scripts/render_report.py` -> `exports/report.html`
- Finish-line check for the first lab: `uv run scripts/lab_check.py`

## Layout
- `sql/<layer>/NN_name.sql`: all transformations. `src/dwhpulse/`: Python orchestration.
- `docs/confluence/`: process pages. `tickets/`: the tickets. `powerbi/model.md`: Power BI model.
- `solutions/` holds reference solutions for the tickets: never read or copy from it unless the user asks.
- Skills live in `.agents/skills/`, see `.agents/README.md`.

(Deliberately thin. You improve this file in Part 2 of the lab.)
