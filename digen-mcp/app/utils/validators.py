"""Validation helpers for media URLs and metadata."""

from __future__ import annotations

from urllib.parse import urlparse

from app.models.errors import DigenError
from app.utils.mime import is_supported_fps_mime, is_supported_image_mime, is_supported_video_mime

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.webm'}


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise DigenError('INVALID_INPUT', 'URL must be an absolute http(s) URL.', retryable=False)
    return parsed.path.lower()


def validate_image_url(url: str) -> None:
    path = _validate_url(url)
    if not any(path.endswith(ext) for ext in IMAGE_EXTENSIONS):
        raise DigenError('INVALID_FILE', 'Image URL must end with jpg, jpeg, png, or webp.', retryable=False)


def validate_video_url(url: str) -> None:
    path = _validate_url(url)
    if not any(path.endswith(ext) for ext in VIDEO_EXTENSIONS):
        raise DigenError('INVALID_FILE', 'Video URL must end with mp4, mov, avi, or webm.', retryable=False)


def validate_media_metadata(*, mime_type: str | None, file_size_bytes: int | None, mode: str) -> None:
    if mime_type is None and file_size_bytes is None:
        return
    if mode == 'image_upscale':
        if mime_type and not is_supported_image_mime(mime_type):
            raise DigenError('INVALID_FILE', 'Unsupported image MIME type for upscaling.', False)
        if file_size_bytes and file_size_bytes > 10 * 1024 * 1024:
            raise DigenError('INVALID_FILE', 'Image upload exceeds 10 MB.', False)
    elif mode == 'video_upscale':
        if mime_type and not is_supported_video_mime(mime_type):
            raise DigenError('INVALID_FILE', 'Unsupported video MIME type for upscaling.', False)
        if file_size_bytes and file_size_bytes > 30 * 1024 * 1024:
            raise DigenError('INVALID_FILE', 'Video upload exceeds 30 MB.', False)
    elif mode == 'boost_fps':
        if mime_type and not is_supported_fps_mime(mime_type):
            raise DigenError('INVALID_FILE', 'FPS boost accepts MP4 only.', False)
        if file_size_bytes and file_size_bytes > 30 * 1024 * 1024:
            raise DigenError('INVALID_FILE', 'FPS boost upload exceeds 30 MB.', False)
    else:
        raise DigenError('INVALID_INPUT', f'Unknown validation mode: {mode}', False)
