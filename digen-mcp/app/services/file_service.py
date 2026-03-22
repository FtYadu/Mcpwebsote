"""File and upload validation utilities."""

from __future__ import annotations

from app.utils.validators import validate_media_metadata


class FileService:
    """Coordinates input media validation rules."""

    def validate_for_image_upscale(self, mime_type: str | None = None, file_size_bytes: int | None = None) -> None:
        validate_media_metadata(mime_type=mime_type, file_size_bytes=file_size_bytes, mode='image_upscale')

    def validate_for_video_upscale(self, mime_type: str | None = None, file_size_bytes: int | None = None) -> None:
        validate_media_metadata(mime_type=mime_type, file_size_bytes=file_size_bytes, mode='video_upscale')

    def validate_for_fps_boost(self, mime_type: str | None = None, file_size_bytes: int | None = None) -> None:
        validate_media_metadata(mime_type=mime_type, file_size_bytes=file_size_bytes, mode='boost_fps')
