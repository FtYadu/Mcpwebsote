import pytest

from app.config import Settings
from app.models.errors import DigenError
from app.providers.mock_provider import MockProvider
from app.services.provider_router import ProviderRouter


def test_provider_router_selects_mock(tmp_path):
    settings = Settings(provider='mock', db_path=str(tmp_path / 'jobs.db'))
    router = ProviderRouter(settings)
    assert isinstance(router.provider, MockProvider)


def test_provider_router_rejects_unknown_provider(tmp_path):
    settings = Settings(provider='unknown', db_path=str(tmp_path / 'jobs.db'))
    with pytest.raises(DigenError):
        ProviderRouter(settings)
