"""HTTP API provider implementation with retries and normalized errors."""

from __future__ import annotations

import logging
from typing import Any

import httpx

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
from app.utils.timeouts import retry_policy

LOGGER = logging.getLogger(__name__)


class APIProvider(BaseProvider):
    """Provider that delegates to a configured HTTP API surface."""

    name = 'api'

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if not settings.api_base_url:
            raise DigenError('PROVIDER_UNAVAILABLE', 'DIGEN_API_BASE_URL must be configured for APIProvider.', False)
        headers = {'Content-Type': 'application/json'}
        if settings.api_token:
            headers['Authorization'] = f'Bearer {settings.api_token}'
        self._client = httpx.Client(
            base_url=settings.api_base_url.rstrip('/'),
            timeout=settings.request_timeout_seconds,
            headers=headers,
        )

    @retry_policy(attempts=3)
    def _send_request(self, method: str, path: str, json_payload: dict[str, Any] | None = None) -> httpx.Response:
        return self._client.request(method, path, json=json_payload)

    def _request(self, method: str, path: str, json_payload: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self._send_request(method, path, json_payload)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise DigenError('PROVIDER_UNAVAILABLE', 'Provider returned a non-object JSON payload.', False)
            return payload
        except httpx.TimeoutException as exc:
            raise DigenError('PROVIDER_TIMEOUT', 'Provider request timed out.', True) from exc
        except httpx.HTTPStatusError as exc:
            LOGGER.warning('provider http error status=%s', exc.response.status_code)
            if exc.response.status_code in {401, 403}:
                raise DigenError('AUTH_REQUIRED', 'Provider authentication failed.', False) from exc
            raise DigenError('PROVIDER_UNAVAILABLE', 'Provider returned an error response.', True) from exc
        except httpx.HTTPError as exc:
            raise DigenError('PROVIDER_UNAVAILABLE', 'Provider request failed.', True) from exc

    def _post_model(self, path: str, payload: Any, schema: type[Any]) -> Any:
        data = self._request('POST', path, json_payload=payload.model_dump(mode='json'))
        return schema.model_validate(data)

    def generate_image(self, payload: GenerateImageInput) -> JobAcceptedOutput:
        return self._post_model('/generate-image', payload, JobAcceptedOutput)

    def edit_image(self, payload: EditImageInput) -> JobAcceptedOutput:
        return self._post_model('/edit-image', payload, JobAcceptedOutput)

    def text_to_video(self, payload: TextToVideoInput) -> JobAcceptedOutput:
        return self._post_model('/text-to-video', payload, JobAcceptedOutput)

    def image_to_video(self, payload: ImageToVideoInput) -> JobAcceptedOutput:
        return self._post_model('/image-to-video', payload, JobAcceptedOutput)

    def upscale_image(self, payload: UpscaleImageInput) -> JobAcceptedOutput:
        return self._post_model('/upscale-image', payload, JobAcceptedOutput)

    def upscale_video(self, payload: UpscaleVideoInput) -> JobAcceptedOutput:
        return self._post_model('/upscale-video', payload, JobAcceptedOutput)

    def boost_fps(self, payload: BoostFpsInput) -> JobAcceptedOutput:
        return self._post_model('/boost-fps', payload, JobAcceptedOutput)

    def get_job_status(self, payload: JobLookupInput) -> JobStatusOutput:
        return self._post_model('/job-status', payload, JobStatusOutput)

    def download_result(self, payload: JobLookupInput) -> DownloadResultOutput:
        return self._post_model('/download-result', payload, DownloadResultOutput)

    def list_models(self) -> ListModelsOutput:
        return ListModelsOutput.model_validate(self._request('GET', '/models'))

    def list_tools(self) -> ListToolsOutput:
        return ListToolsOutput.model_validate(self._request('GET', '/tools'))

    def get_account_credits(self) -> AccountCreditsOutput:
        return AccountCreditsOutput.model_validate(self._request('GET', '/account/credits'))
