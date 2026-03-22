"""Pydantic tool input schemas."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.utils.validators import validate_image_url, validate_video_url


class BaseInputModel(BaseModel):
    """Base class for all tool inputs."""

    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class UpscaleFactor(str, Enum):
    """Supported upscaling factors."""

    x2 = '2x'
    x4 = '4x'


class GenerateImageInput(BaseInputModel):
    prompt: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    aspect_ratio: str | None = None
    reference_images: list[HttpUrl] = Field(default_factory=list)


class EditImageInput(BaseInputModel):
    image_url: HttpUrl
    prompt: str = Field(min_length=1, max_length=4000)
    model: str | None = None

    @field_validator('image_url')
    @classmethod
    def _validate_image(cls, value: HttpUrl) -> HttpUrl:
        validate_image_url(str(value))
        return value


class TextToVideoInput(BaseInputModel):
    prompt: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1, le=120)
    aspect_ratio: str | None = None
    resolution: str | None = None


class ImageToVideoInput(BaseInputModel):
    image_url: HttpUrl
    prompt: str = Field(min_length=1, max_length=4000)
    model: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1, le=120)
    resolution: str | None = None

    @field_validator('image_url')
    @classmethod
    def _validate_image(cls, value: HttpUrl) -> HttpUrl:
        validate_image_url(str(value))
        return value


class UpscaleImageInput(BaseInputModel):
    image_url: HttpUrl
    factor: UpscaleFactor

    @field_validator('image_url')
    @classmethod
    def _validate_image(cls, value: HttpUrl) -> HttpUrl:
        validate_image_url(str(value))
        return value


class UpscaleVideoInput(BaseInputModel):
    video_url: HttpUrl
    factor: UpscaleFactor

    @field_validator('video_url')
    @classmethod
    def _validate_video(cls, value: HttpUrl) -> HttpUrl:
        validate_video_url(str(value))
        return value


class BoostFpsInput(BaseInputModel):
    video_url: HttpUrl

    @field_validator('video_url')
    @classmethod
    def _validate_video(cls, value: HttpUrl) -> HttpUrl:
        validate_video_url(str(value))
        return value


class JobLookupInput(BaseInputModel):
    job_id: str = Field(min_length=1)


class SummarizeTextInput(BaseInputModel):
    text: str = Field(min_length=1, max_length=20000)
    max_sentences: int = Field(default=3, ge=1, le=10)


class SentimentAnalysisInput(BaseInputModel):
    text: str = Field(min_length=1, max_length=20000)


class DocumentToTextInput(BaseInputModel):
    content: str = Field(min_length=1, max_length=50000)
    content_type: str = Field(default='text/plain')


class TextToSpeechInput(BaseInputModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str = Field(default='alloy')
    format: str = Field(default='mp3')


class TranscriptionInput(BaseInputModel):
    audio_url: HttpUrl
    language: str | None = None


class ToolExecutionRequest(BaseInputModel):
    tool: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)


class WorkflowTaskInput(BaseInputModel):
    id: int = Field(ge=1)
    tool: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[int] = Field(default_factory=list)


class WorkflowSubmissionInput(BaseInputModel):
    tasks: list[WorkflowTaskInput] = Field(min_length=1)

    @field_validator('tasks')
    @classmethod
    def _validate_unique_ids(cls, value: list[WorkflowTaskInput]) -> list[WorkflowTaskInput]:
        task_ids = [task.id for task in value]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError('Each workflow task id must be unique.')
        return value
