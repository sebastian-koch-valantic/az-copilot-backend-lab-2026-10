"""One in-memory connection with every schema attached as its own SQLite file.

SQLite has no schemas, so each Oracle schema (SRC, STG, CORE, MART, CTL) is a separate
database file. SQL can then say `core.orders`, as it would on Oracle.
"""

import sqlite3
from pathlib import Path

from dwhpulse import config


def connect(data_dir: Path | str | None = None) -> sqlite3.Connection:
    directory = Path(data_dir) if data_dir else config.data_dir()
    directory.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for schema in config.SCHEMAS:
        conn.execute(f"ATTACH DATABASE ? AS {schema}", (str(directory / f"{schema}.db"),))
    return conn
