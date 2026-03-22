import pytest
from pydantic import ValidationError

from app.models.errors import DigenError
from app.models.tool_inputs import GenerateImageInput, UpscaleImageInput, UpscaleVideoInput
from app.utils.validators import validate_media_metadata


def test_generate_image_schema_accepts_reference_images():
    payload = GenerateImageInput(
        prompt='hello',
        model='mock-image-v1',
        aspect_ratio='1:1',
        reference_images=['https://example.com/reference.png'],
    )
    assert payload.reference_images[0].path == '/reference.png'


def test_upscale_image_schema_rejects_invalid_extension():
    with pytest.raises((ValidationError, DigenError)):
        UpscaleImageInput(image_url='https://example.com/file.gif', factor='2x')


def test_upscale_video_schema_rejects_invalid_extension():
    with pytest.raises((ValidationError, DigenError)):
        UpscaleVideoInput(video_url='https://example.com/file.mkv', factor='2x')


def test_metadata_validation_enforces_limits():
    with pytest.raises(DigenError):
        validate_media_metadata(mime_type='image/png', file_size_bytes=11 * 1024 * 1024, mode='image_upscale')
