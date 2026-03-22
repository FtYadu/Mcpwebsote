"""MCP resource for upload limits."""

from __future__ import annotations

UPLOAD_LIMITS = {
    'image_upscaler': {
        'mime_types': ['image/jpeg', 'image/png', 'image/webp'],
        'extensions': ['jpg', 'jpeg', 'png', 'webp'],
        'max_size_mb': 10,
    },
    'video_upscaler': {
        'mime_types': ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'],
        'extensions': ['mp4', 'mov', 'avi', 'webm'],
        'max_size_mb': 30,
    },
    'fps_booster': {
        'mime_types': ['video/mp4'],
        'extensions': ['mp4'],
        'max_size_mb': 30,
    },
}


def get_limits_resource() -> dict:
    text = (
        'Upload limits: image upscaler supports JPG/JPEG/PNG/WEBP up to 10 MB; '
        'video upscaler supports MP4/MOV/AVI/WEBM up to 30 MB; '
        'FPS booster supports MP4 up to 30 MB.'
    )
    return {'text': text, 'limits': UPLOAD_LIMITS}
