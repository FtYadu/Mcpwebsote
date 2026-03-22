"""Deterministic mock provider for local development and tests."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.errors import DigenError
from app.models.jobs import JobStatus
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
    ModelInfo,
    ToolInfo,
)
from app.providers.base import BaseProvider
from app.services.file_service import FileService


@dataclass
class MockJobState:
    tool_name: str
    job_id: str


class MockProvider(BaseProvider):
    """Mock implementation that simulates a predictable job lifecycle."""

    name = 'mock'

    def __init__(self) -> None:
        self._jobs: dict[str, MockJobState] = {}
        self._status_polls: dict[str, int] = {}
        self._file_service = FileService()

    def _make_job_id(self, tool_name: str) -> str:
        counter = sum(1 for job in self._jobs.values() if job.tool_name == tool_name) + 1
        return f'job-{tool_name}-{counter:04d}'

    def _accept_job(self, tool_name: str, model: str | None = None) -> JobAcceptedOutput:
        job_id = self._make_job_id(tool_name)
        self._jobs[job_id] = MockJobState(tool_name=tool_name, job_id=job_id)
        self._status_polls[job_id] = 0
        return JobAcceptedOutput(
            job_id=job_id,
            status=JobStatus.queued,
            model=model,
            preview_url=f'https://mock.digen.local/previews/{job_id}.jpg',
            result_url=None,
        )

    def generate_image(self, payload: GenerateImageInput) -> JobAcceptedOutput:
        return self._accept_job('generate_image', payload.model or 'mock-image-v1')

    def edit_image(self, payload: EditImageInput) -> JobAcceptedOutput:
        return self._accept_job('edit_image', payload.model or 'mock-edit-v1')

    def text_to_video(self, payload: TextToVideoInput) -> JobAcceptedOutput:
        return self._accept_job('text_to_video', payload.model or 'mock-video-v1')

    def image_to_video(self, payload: ImageToVideoInput) -> JobAcceptedOutput:
        return self._accept_job('image_to_video', payload.model or 'mock-video-v1')

    def upscale_image(self, payload: UpscaleImageInput) -> JobAcceptedOutput:
        self._file_service.validate_for_image_upscale(mime_type='image/png', file_size_bytes=1024)
        return self._accept_job('upscale_image', 'mock-upscale-image-v1')

    def upscale_video(self, payload: UpscaleVideoInput) -> JobAcceptedOutput:
        self._file_service.validate_for_video_upscale(mime_type='video/mp4', file_size_bytes=1024)
        return self._accept_job('upscale_video', 'mock-upscale-video-v1')

    def boost_fps(self, payload: BoostFpsInput) -> JobAcceptedOutput:
        self._file_service.validate_for_fps_boost(mime_type='video/mp4', file_size_bytes=1024)
        return self._accept_job('boost_fps', 'mock-fps-v1')

    def get_job_status(self, payload: JobLookupInput) -> JobStatusOutput:
        if payload.job_id not in self._jobs:
            raise DigenError('JOB_NOT_FOUND', 'No job exists for the supplied job_id.', False)
        poll_count = self._status_polls[payload.job_id]
        self._status_polls[payload.job_id] = poll_count + 1
        if poll_count == 0:
            return JobStatusOutput(
                job_id=payload.job_id,
                status=JobStatus.processing,
                progress=50,
                stage='rendering',
                preview_url=f'https://mock.digen.local/previews/{payload.job_id}.jpg',
                result_url=None,
                error=None,
            )
        return JobStatusOutput(
            job_id=payload.job_id,
            status=JobStatus.completed,
            progress=100,
            stage='done',
            preview_url=f'https://mock.digen.local/previews/{payload.job_id}.jpg',
            result_url=f'https://mock.digen.local/results/{payload.job_id}.bin',
            error=None,
        )

    def download_result(self, payload: JobLookupInput) -> DownloadResultOutput:
        if payload.job_id not in self._jobs:
            raise DigenError('JOB_NOT_FOUND', 'No job exists for the supplied job_id.', False)
        if self._status_polls.get(payload.job_id, 0) < 2:
            raise DigenError('JOB_NOT_READY', 'Job result is not ready yet.', True)
        return DownloadResultOutput(
            job_id=payload.job_id,
            status=JobStatus.completed,
            result_url=f'https://mock.digen.local/results/{payload.job_id}.bin',
            thumbnail_url=f'https://mock.digen.local/thumbs/{payload.job_id}.jpg',
            mime_type='application/octet-stream',
            expires_at='2099-01-01T00:00:00Z',
        )

    def list_models(self) -> ListModelsOutput:
        return ListModelsOutput(models=[
            ModelInfo(id='mock-image-v1', category='image', description='Deterministic mock image generator'),
            ModelInfo(id='mock-edit-v1', category='image', description='Deterministic mock image editor'),
            ModelInfo(id='mock-video-v1', category='video', description='Deterministic mock video generator'),
            ModelInfo(id='mock-upscale-image-v1', category='utility', description='Deterministic image upscaler'),
            ModelInfo(id='mock-upscale-video-v1', category='utility', description='Deterministic video upscaler'),
            ModelInfo(id='mock-fps-v1', category='utility', description='Deterministic FPS booster'),
        ])

    def list_tools(self) -> ListToolsOutput:
        return ListToolsOutput(tools=[
            ToolInfo(name='generate_image', description='Generate a still image from text'),
            ToolInfo(name='edit_image', description='Edit an existing image from text'),
            ToolInfo(name='text_to_video', description='Generate video from text'),
            ToolInfo(name='image_to_video', description='Animate an image into a video'),
            ToolInfo(name='upscale_image', description='Upscale an image by 2x or 4x'),
            ToolInfo(name='upscale_video', description='Upscale a video by 2x or 4x'),
            ToolInfo(name='boost_fps', description='Increase video framerate'),
            ToolInfo(name='get_job_status', description='Poll async job status'),
            ToolInfo(name='download_result', description='Resolve a completed job output'),
            ToolInfo(name='list_models', description='List provider model identifiers'),
            ToolInfo(name='list_tools', description='List provider tool support'),
            ToolInfo(name='get_account_credits', description='Read account credit balance'),
        ])

    def get_account_credits(self) -> AccountCreditsOutput:
        return AccountCreditsOutput(provider=self.name, credits_remaining=1000, credits_total=1000, currency='credits')
