"""Playwright fallback provider scaffold.

This module intentionally avoids shipping brittle scraping logic.
Use it only when no documented API provider is available and only for authenticated,
user-owned access boundaries.
"""

from __future__ import annotations

from app.config import Settings
from app.models.errors import DigenError
from app.models.tool_inputs import (
    BoostFpsInput,
    EditImageInput,
    GenerateImageInput,
    ImageToVideoInput,
    JobLookupInput,
    TextToVideoInput,
    UpscaleImageInput,
    UpscaleVideoInput,
)
from app.models.tool_outputs import (
    AccountCreditsOutput,
    DownloadResultOutput,
    JobAcceptedOutput,
    JobStatusOutput,
    ListModelsOutput,
    ListToolsOutput,
)
from app.providers.base import BaseProvider

LOGIN_URL_PATH = '/login'
DASHBOARD_PATH = '/dashboard'


class PlaywrightProvider(BaseProvider):
    """Fallback browser-automation provider.

    TODO: Implement resilient navigation and session persistence using explicit selectors
    stored in constants or a versioned config layer.
    TODO: Enforce per-user auth boundaries before any session is loaded.
    TODO: Add rate limiting hook points before page actions to protect user-specific accounts.
    """

    name = 'playwright'

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _unsupported(self) -> DigenError:
        return DigenError(
            'PROVIDER_UNAVAILABLE',
            'Playwright fallback is scaffolded only. Add site-specific automation behind this provider.',
            False,
        )

    def generate_image(self, payload: GenerateImageInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def edit_image(self, payload: EditImageInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def text_to_video(self, payload: TextToVideoInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def image_to_video(self, payload: ImageToVideoInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def upscale_image(self, payload: UpscaleImageInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def upscale_video(self, payload: UpscaleVideoInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def boost_fps(self, payload: BoostFpsInput) -> JobAcceptedOutput:
        raise self._unsupported()

    def get_job_status(self, payload: JobLookupInput) -> JobStatusOutput:
        raise self._unsupported()

    def download_result(self, payload: JobLookupInput) -> DownloadResultOutput:
        raise self._unsupported()

    def list_models(self) -> ListModelsOutput:
        raise self._unsupported()

    def list_tools(self) -> ListToolsOutput:
        raise self._unsupported()

    def get_account_credits(self) -> AccountCreditsOutput:
        raise self._unsupported()
