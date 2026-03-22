"""Pydantic tool input schemas."""

from __future__ import annotations

from enum import Enum

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
