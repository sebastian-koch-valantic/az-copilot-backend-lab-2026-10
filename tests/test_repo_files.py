import subprocess
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_local_data_is_git_ignored():
    if not (ROOT / ".git").exists():
        return
    for path in ("data/x.db", "exports/x.csv", ".env"):
        assert subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", path]).returncode == 0
