"""Provider abstraction for Digen-style creative workflows."""

from __future__ import annotations

from abc import ABC, abstractmethod

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


class BaseProvider(ABC):
    """Abstract provider interface."""

    name: str

    @abstractmethod
    def generate_image(self, payload: GenerateImageInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def edit_image(self, payload: EditImageInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def text_to_video(self, payload: TextToVideoInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def image_to_video(self, payload: ImageToVideoInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def upscale_image(self, payload: UpscaleImageInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def upscale_video(self, payload: UpscaleVideoInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def boost_fps(self, payload: BoostFpsInput) -> JobAcceptedOutput: ...

    @abstractmethod
    def get_job_status(self, payload: JobLookupInput) -> JobStatusOutput: ...

    @abstractmethod
    def download_result(self, payload: JobLookupInput) -> DownloadResultOutput: ...

    @abstractmethod
    def list_models(self) -> ListModelsOutput: ...

    @abstractmethod
    def list_tools(self) -> ListToolsOutput: ...

    @abstractmethod
    def get_account_credits(self) -> AccountCreditsOutput: ...
