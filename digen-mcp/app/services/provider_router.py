"""Provider selection and routing."""

from __future__ import annotations

from app.models.errors import DigenError
from app.providers.api_provider import APIProvider
from app.providers.mock_provider import MockProvider
from app.providers.playwright_provider import PlaywrightProvider


class ProviderRouter:
    """Selects the active provider implementation from configuration."""

    def __init__(self, settings) -> None:
        self._settings = settings
        self._provider = self._build_provider()

    def _build_provider(self):
        provider_name = self._settings.provider.lower()
        if provider_name == 'mock':
            return MockProvider()
        if provider_name == 'api':
            return APIProvider(self._settings)
        if provider_name == 'playwright':
            return PlaywrightProvider(self._settings)
        raise DigenError('PROVIDER_UNAVAILABLE', f'Unsupported provider: {provider_name}', False)

    @property
    def provider(self):
        return self._provider
