"""Error models and helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    """Standardized error payload."""

    model_config = ConfigDict(extra='forbid')

    code: str
    message: str
    retryable: bool = False


class ErrorEnvelope(BaseModel):
    """Top-level error envelope."""

    model_config = ConfigDict(extra='forbid')

    error: ErrorDetail


class DigenError(Exception):
    """Base application exception that carries a structured error."""

    def __init__(self, code: str, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.detail = ErrorDetail(code=code, message=message, retryable=retryable)

    def to_envelope(self) -> ErrorEnvelope:
        """Convert exception into a serializable envelope."""

        return ErrorEnvelope(error=self.detail)
