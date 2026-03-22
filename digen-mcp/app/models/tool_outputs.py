"""Pydantic tool output schemas."""

from __future__ import annotations

from typing import Any, Literal

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
    category: Literal['image', 'video', 'utility', 'text', 'speech', 'document']
    description: str


class ListModelsOutput(BaseOutputModel):
    models: list[ModelInfo]


class ToolInfo(BaseModel):
    name: str
    supports_async: bool = True
    description: str
    category: Literal['image', 'video', 'utility', 'text', 'speech', 'document', 'workflow'] = 'utility'
    input_schema: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class ListToolsOutput(BaseOutputModel):
    tools: list[ToolInfo]


class AccountCreditsOutput(BaseOutputModel):
    provider: str
    credits_remaining: int | None = None
    credits_total: int | None = None
    currency: str | None = None
    error: ErrorDetail | None = None


class TextSummaryOutput(BaseOutputModel):
    summary: str
    sentence_count: int


class SentimentAnalysisOutput(BaseOutputModel):
    sentiment: Literal['positive', 'neutral', 'negative']
    score: float = Field(ge=-1.0, le=1.0)
    rationale: str


class DocumentTextOutput(BaseOutputModel):
    text: str
    content_type: str
    extraction_method: str


class TextToSpeechOutput(BaseOutputModel):
    audio_url: HttpUrl
    voice: str
    format: str


class TranscriptionOutput(BaseOutputModel):
    transcript: str
    language: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class WorkflowTaskResult(BaseModel):
    id: int
    tool: str
    status: Literal['completed', 'failed', 'skipped']
    output: dict[str, Any] | None = None
    error: ErrorDetail | None = None


class WorkflowExecutionOutput(BaseOutputModel):
    workflow_id: str
    status: Literal['completed', 'failed']
    tasks: list[WorkflowTaskResult]
