from __future__ import annotations

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest  # noqa: E402
from core.config import get_settings  # noqa: E402
from database.connection import get_connection  # noqa: E402


@pytest.fixture
def test_db(tmp_path: Path):
    db_path = tmp_path / "test.db"
    original = get_settings().DATABASE_URL
    get_settings().DATABASE_URL = f"sqlite:///{db_path}"
    from database.db import init_db
    init_db()
    yield db_path
    get_settings().DATABASE_URL = original
    if db_path.exists():
        db_path.unlink()
