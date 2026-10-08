"""Paths and constants. The only module that reads the environment."""

import os
from pathlib import Path

SCHEMAS = ("src", "stg", "core", "mart", "ctl")
ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"

# A step that finishes after this time of day counts as late (see docs/confluence/pipeline-operations.md).
DAILY_DEADLINE = "06:00"


def data_dir() -> Path:
    return Path(os.environ.get("DWH_DATA_DIR", ROOT / "data"))
