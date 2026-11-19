import pytest

import app

COUNTER_FILENAME = "visits.txt"


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Functions read module globals at call time, so setattr is enough; no reload needed.
    monkeypatch.setattr(app, "COUNTER_FILE", tmp_path / COUNTER_FILENAME)
    monkeypatch.setattr(app, "DATABASE_URL", None)
    return app.app.test_client()
