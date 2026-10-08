"""Repository conventions, enforced as tests."""

from dwhpulse import config
from dwhpulse.pipeline import STEPS


def sql_files():
    return sorted(p for p in config.SQL_DIR.rglob("*.sql"))


def test_every_sql_file_belongs_to_a_step():
    declared = {config.SQL_DIR / step.sql_file for step in STEPS}
    assert set(sql_files()) == declared


def test_no_select_star():
    for path in sql_files():
        assert "SELECT *" not in path.read_text(encoding="utf-8").upper(), path.name


def test_only_stg_reads_from_src():
    for path in sql_files():
        text = path.read_text(encoding="utf-8").lower()
        if "stg/" not in path.as_posix():
            assert "src." not in text, path.name


def test_no_sql_writes_to_src():
    for path in sql_files():
        text = path.read_text(encoding="utf-8").upper()
        for verb in ("INSERT INTO SRC.", "UPDATE SRC.", "DELETE FROM SRC.", "DROP TABLE IF EXISTS SRC."):
            assert verb not in text, path.name
