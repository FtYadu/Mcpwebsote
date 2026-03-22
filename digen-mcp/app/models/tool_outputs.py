"""Pydantic tool output schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.errors import ErrorDetail
from app.models.jobs import JobStatus


class BaseOutputModel(BaseModel):
    """Base class for tool outputs."""

    model_config = ConfigDict(extra='forbid')


class JobAcceptedOutput(BaseOutputModel):
    job_id: str
    status: JobStatus
    model: str | None = None
    preview_url: HttpUrl | None = None
    result_url: HttpUrl | None = None


class JobStatusOutput(BaseOutputModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    stage: str | None = None
    preview_url: HttpUrl | None = None
    result_url: HttpUrl | None = None
    error: ErrorDetail | None = None


class DownloadResultOutput(BaseOutputModel):
    job_id: str
    status: JobStatus
    result_url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None
    mime_type: str | None = None
    expires_at: str | None = None


class ModelInfo(BaseModel):
    id: str
    category: Literal['image', 'video', 'utility']
    description: str


class ListModelsOutput(BaseOutputModel):
    models: list[ModelInfo]


class ToolInfo(BaseModel):
    name: str
    supports_async: bool = True
    description: str


class ListToolsOutput(BaseOutputModel):
    tools: list[ToolInfo]


class AccountCreditsOutput(BaseOutputModel):
    provider: str
    credits_remaining: int | None = None
    credits_total: int | None = None
    currency: str | None = None
    error: ErrorDetail | None = None
