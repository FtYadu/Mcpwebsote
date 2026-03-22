"""MIME type allowlists and helper utilities."""

from __future__ import annotations

IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
VIDEO_MIME_TYPES = {'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'}
FPS_VIDEO_MIME_TYPES = {'video/mp4'}


def is_supported_image_mime(mime_type: str) -> bool:
    return mime_type.lower() in IMAGE_MIME_TYPES


def is_supported_video_mime(mime_type: str) -> bool:
    return mime_type.lower() in VIDEO_MIME_TYPES


def is_supported_fps_mime(mime_type: str) -> bool:
    return mime_type.lower() in FPS_VIDEO_MIME_TYPES
