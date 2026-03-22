"""Timeout and retry helpers."""

from __future__ import annotations

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


def retry_policy(attempts: int):
    """Return a tenacity retry decorator for transient provider errors."""

    return retry(
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        stop=stop_after_attempt(max(attempts, 1)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        reraise=True,
    )
