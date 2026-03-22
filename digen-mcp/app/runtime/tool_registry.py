"""Plugin-style tool registry for MCP and HTTP surfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Type

from pydantic import BaseModel

from app.models.errors import DigenError
from app.models.tool_inputs import (
    BoostFpsInput,
    DocumentToTextInput,
    EditImageInput,
    GenerateImageInput,
    ImageToVideoInput,
    JobLookupInput,
    SentimentAnalysisInput,
    SummarizeTextInput,
    TextToSpeechInput,
    TextToVideoInput,
    TranscriptionInput,
    UpscaleImageInput,
    UpscaleVideoInput,
)
from app.models.tool_outputs import ToolInfo
from app.services.analysis_service import AnalysisService
from app.services.job_service import JobService


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str
    category: str
    input_model: Type[BaseModel] | None
    handler: Callable[[Any], BaseModel]
    supports_async: bool = False
    tags: list[str] = field(default_factory=list)

    def metadata(self) -> ToolInfo:
        schema = self.input_model.model_json_schema() if self.input_model else {}
        return ToolInfo(
            name=self.name,
            description=self.description,
            category=self.category,
            supports_async=self.supports_async,
            input_schema=schema,
            tags=self.tags,
        )


class ToolRegistry:
    """Registry with dynamic lookup, validation, and execution helpers."""

    def __init__(self, analysis_service: AnalysisService, provider: Any, job_service: JobService, public_base_url: str) -> None:
        self._analysis_service = analysis_service
        self._provider = provider
        self._job_service = job_service
        self._public_base_url = public_base_url
        self._tools: dict[str, ToolDefinition] = {}
        self._register_provider_tools()
        self._register_utility_tools()

    @property
    def count(self) -> int:
        return len(self._tools)

    def list_metadata(self) -> list[ToolInfo]:
        return [tool.metadata() for tool in self._tools.values()]

    def get_definition(self, name: str) -> ToolDefinition:
        tool = self._tools.get(name)
        if tool is None:
            raise DigenError('UNKNOWN_TOOL', f'The tool {name!r} is not registered.', False)
        return tool

    def execute(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        tool = self.get_definition(name)
        model = tool.input_model.model_validate(payload) if tool.input_model else None
        output = tool.handler(model)
        return output.model_dump(mode='json')

    def _register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def _register_provider_tools(self) -> None:
        async_tags = ['provider', 'job']
        self._register(ToolDefinition('generate_image', 'Generate a still image from text.', 'image', GenerateImageInput, lambda p: self._job_service.record_acceptance('generate_image', p.model_dump(mode='json'), self._provider.generate_image(p)), True, async_tags + ['generation']))
        self._register(ToolDefinition('edit_image', 'Edit an image with an instruction prompt.', 'image', EditImageInput, lambda p: self._job_service.record_acceptance('edit_image', p.model_dump(mode='json'), self._provider.edit_image(p)), True, async_tags + ['editing']))
        self._register(ToolDefinition('text_to_video', 'Generate a video from text.', 'video', TextToVideoInput, lambda p: self._job_service.record_acceptance('text_to_video', p.model_dump(mode='json'), self._provider.text_to_video(p)), True, async_tags + ['generation']))
        self._register(ToolDefinition('image_to_video', 'Animate an image into a video.', 'video', ImageToVideoInput, lambda p: self._job_service.record_acceptance('image_to_video', p.model_dump(mode='json'), self._provider.image_to_video(p)), True, async_tags + ['generation']))
        self._register(ToolDefinition('upscale_image', 'Upscale an image by 2x or 4x.', 'utility', UpscaleImageInput, lambda p: self._job_service.record_acceptance('upscale_image', p.model_dump(mode='json'), self._provider.upscale_image(p)), True, async_tags + ['upscale']))
        self._register(ToolDefinition('upscale_video', 'Upscale a video by 2x or 4x.', 'utility', UpscaleVideoInput, lambda p: self._job_service.record_acceptance('upscale_video', p.model_dump(mode='json'), self._provider.upscale_video(p)), True, async_tags + ['upscale']))
        self._register(ToolDefinition('boost_fps', 'Increase video frame rate.', 'utility', BoostFpsInput, lambda p: self._job_service.record_acceptance('boost_fps', p.model_dump(mode='json'), self._provider.boost_fps(p)), True, async_tags + ['video']))
        self._register(ToolDefinition('get_job_status', 'Read the latest provider status for a job.', 'workflow', JobLookupInput, lambda p: self._job_service.update_status(self._provider.get_job_status(p)), False, ['provider', 'job', 'status']))
        self._register(ToolDefinition('download_result', 'Resolve the final artifact URL for a completed job.', 'workflow', JobLookupInput, lambda p: self._job_service.store_download(self._provider.download_result(p)), False, ['provider', 'job', 'artifact']))
        self._register(ToolDefinition('list_models', 'List provider model identifiers.', 'workflow', None, lambda _: self._provider.list_models(), False, ['provider', 'catalog'] ))
        self._register(ToolDefinition('list_tools', 'List provider-native tools.', 'workflow', None, lambda _: self._provider.list_tools(), False, ['provider', 'catalog']))
        self._register(ToolDefinition('get_account_credits', 'Read account credit balances.', 'workflow', None, lambda _: self._provider.get_account_credits(), False, ['provider', 'account']))

    def _register_utility_tools(self) -> None:
        self._register(ToolDefinition('summarize_text', 'Summarize long-form text for downstream agent planning.', 'text', SummarizeTextInput, lambda p: self._analysis_service.summarize_text(p.text, p.max_sentences), False, ['local', 'nlp', 'summary']))
        self._register(ToolDefinition('analyze_sentiment', 'Estimate overall sentiment for a block of text.', 'text', SentimentAnalysisInput, lambda p: self._analysis_service.analyze_sentiment(p.text), False, ['local', 'nlp', 'sentiment']))
        self._register(ToolDefinition('document_to_text', 'Normalize document or OCR text into structured plain text.', 'document', DocumentToTextInput, lambda p: self._analysis_service.document_to_text(p.content, p.content_type), False, ['local', 'document']))
        self._register(ToolDefinition('text_to_speech', 'Create a speech artifact URL from text input.', 'speech', TextToSpeechInput, lambda p: self._analysis_service.text_to_speech(p.text, p.voice, p.format, self._public_base_url), False, ['local', 'speech']))
        self._register(ToolDefinition('transcribe_audio', 'Generate a transcription placeholder for an audio file URL.', 'speech', TranscriptionInput, lambda p: self._analysis_service.transcribe_audio(str(p.audio_url), p.language), False, ['local', 'speech']))
