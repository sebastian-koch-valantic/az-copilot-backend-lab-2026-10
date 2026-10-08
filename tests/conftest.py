import pytest

from dwhpulse import db, seed


@pytest.fixture()
def conn(tmp_path):
    connection = db.connect(tmp_path)
    seed.ensure_control(connection)
    seed.load_source(connection)
    yield connection
    connection.close()
