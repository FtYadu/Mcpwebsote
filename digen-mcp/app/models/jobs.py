"""Shared job and workflow models."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.errors import ErrorDetail


class JobStatus(str, Enum):
    """Lifecycle states for async provider jobs."""

    queued = 'queued'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'
    cancelled = 'cancelled'


class JobRecord(BaseModel):
    """Internal persistent representation of a tool job."""

    model_config = ConfigDict(extra='forbid')

    job_id: str
    tool_name: str
    provider_name: str
    status: JobStatus
    progress: int = Field(default=0, ge=0, le=100)
    stage: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    output_payload: dict[str, Any] = Field(default_factory=dict)
    preview_url: HttpUrl | None = None
    result_url: HttpUrl | None = None
    error: ErrorDetail | None = None


class HealthStatus(BaseModel):
    """Structured health response for dependency introspection."""

    model_config = ConfigDict(extra='forbid')

    status: str
    provider: str
    database: dict[str, Any]
    redis: dict[str, Any]
    tools: dict[str, Any]
    queue: dict[str, Any]
