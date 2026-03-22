# ruff: noqa: E402
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import Settings
from app.runtime.runtime import build_runtime
from app.services.job_service import JobService
from app.services.provider_router import ProviderRouter
from app.storage.db import SQLiteJobStore
from app.storage.redis_client import RedisBackedStateStore


@pytest.fixture()
def mock_settings(tmp_path: Path) -> Settings:
    return Settings(
        provider='mock',
        db_path=str(tmp_path / 'jobs.db'),
        temp_dir=str(tmp_path / 'tmp'),
        redis_url=None,
        public_base_url='http://testserver',
    )


@pytest.fixture()
def runtime_services(mock_settings: Settings):
    provider = ProviderRouter(mock_settings).provider
    db = SQLiteJobStore(mock_settings.db_file)
    transient = RedisBackedStateStore(None)
    jobs = JobService(db, transient, provider.name)
    return provider, jobs


@pytest.fixture()
def test_client(mock_settings: Settings):
    runtime = build_runtime(mock_settings)
    with TestClient(runtime.app) as client:
        yield client
