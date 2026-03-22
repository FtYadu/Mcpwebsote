"""Application runtime assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse

try:  # pragma: no cover - runtime compatibility shim
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover
    class FastMCP:  # type: ignore[override]
        def __init__(self, name: str):
            self.name = name
        def tool(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def resource(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def run(self, *args, **kwargs):
            raise RuntimeError('fastmcp is not installed')

from app.config import Settings
from app.logging_config import configure_logging
from app.models.errors import DigenError
from app.models.jobs import HealthStatus
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
    WorkflowSubmissionInput,
)
from app.resources.account_resource import get_account_resource
from app.resources.limits_resource import get_limits_resource
from app.resources.models_resource import get_models_resource
from app.services.analysis_service import AnalysisService
from app.services.job_service import JobService
from app.services.provider_router import ProviderRouter
from app.services.realtime_service import RealtimeNotifier
from app.services.workflow_service import WorkflowService
from app.storage.db import create_job_store
from app.storage.redis_client import RedisBackedStateStore
from app.runtime.tool_registry import ToolRegistry


@dataclass(slots=True)
class Runtime:
    mcp: FastMCP
    app: FastAPI
    provider: Any
    job_service: JobService
    registry: ToolRegistry
    workflow_service: WorkflowService
    notifier: RealtimeNotifier


class MetricsRegistry:
    """Minimal in-process metrics exporter."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {'workflow_requests_total': 0, 'tool_executions_total': 0}

    def increment(self, key: str, amount: int = 1) -> None:
        self._counters[key] = self._counters.get(key, 0) + amount

    def render(self) -> str:
        return '\n'.join(f'{key} {value}' for key, value in sorted(self._counters.items())) + '\n'


metrics = MetricsRegistry()


def build_runtime(settings: Settings) -> Runtime:
    """Build MCP and HTTP app instances."""

    configure_logging(settings.log_level)
    router = ProviderRouter(settings)
    provider = router.provider
    db = create_job_store(settings.database_url, settings.db_file)
    transient_store = RedisBackedStateStore(settings.redis_url)
    notifier = RealtimeNotifier()
    job_service = JobService(db, transient_store, provider.name, notifier)
    registry = ToolRegistry(AnalysisService(), provider, job_service, settings.public_base_url)
    workflow_service = WorkflowService(registry)

    mcp = FastMCP('digen-mcp')
    app = FastAPI(title='digen-mcp', version='2.0.0')

    def invoke(tool_name: str, payload: dict | None = None) -> dict:
        metrics.increment('tool_executions_total')
        return registry.execute(tool_name, payload or {})

    @mcp.tool()
    def generate_image(payload: GenerateImageInput) -> dict:
        return invoke('generate_image', payload.model_dump(mode='json'))

    @mcp.tool()
    def edit_image(payload: EditImageInput) -> dict:
        return invoke('edit_image', payload.model_dump(mode='json'))

    @mcp.tool()
    def text_to_video(payload: TextToVideoInput) -> dict:
        return invoke('text_to_video', payload.model_dump(mode='json'))

    @mcp.tool()
    def image_to_video(payload: ImageToVideoInput) -> dict:
        return invoke('image_to_video', payload.model_dump(mode='json'))

    @mcp.tool()
    def upscale_image(payload: UpscaleImageInput) -> dict:
        return invoke('upscale_image', payload.model_dump(mode='json'))

    @mcp.tool()
    def upscale_video(payload: UpscaleVideoInput) -> dict:
        return invoke('upscale_video', payload.model_dump(mode='json'))

    @mcp.tool()
    def boost_fps(payload: BoostFpsInput) -> dict:
        return invoke('boost_fps', payload.model_dump(mode='json'))

    @mcp.tool()
    def get_job_status(payload: JobLookupInput) -> dict:
        return invoke('get_job_status', payload.model_dump(mode='json'))

    @mcp.tool()
    def download_result(payload: JobLookupInput) -> dict:
        return invoke('download_result', payload.model_dump(mode='json'))

    @mcp.tool()
    def list_models() -> dict:
        return invoke('list_models')

    @mcp.tool()
    def list_tools() -> dict:
        return invoke('list_tools')

    @mcp.tool()
    def get_account_credits() -> dict:
        return invoke('get_account_credits')

    @mcp.tool()
    def summarize_text(payload: SummarizeTextInput) -> dict:
        return invoke('summarize_text', payload.model_dump(mode='json'))

    @mcp.tool()
    def analyze_sentiment(payload: SentimentAnalysisInput) -> dict:
        return invoke('analyze_sentiment', payload.model_dump(mode='json'))

    @mcp.tool()
    def document_to_text(payload: DocumentToTextInput) -> dict:
        return invoke('document_to_text', payload.model_dump(mode='json'))

    @mcp.tool()
    def text_to_speech(payload: TextToSpeechInput) -> dict:
        return invoke('text_to_speech', payload.model_dump(mode='json'))

    @mcp.tool()
    def transcribe_audio(payload: TranscriptionInput) -> dict:
        return invoke('transcribe_audio', payload.model_dump(mode='json'))

    @mcp.resource('digen://models')
    def models_resource() -> dict:
        return get_models_resource(provider)

    @mcp.resource('digen://tools')
    def tools_resource() -> dict:
        return {'tools': [tool.model_dump(mode='json') for tool in registry.list_metadata()]}

    @mcp.resource('digen://limits/uploads')
    def limits_resource() -> dict:
        return get_limits_resource()

    @mcp.resource('digen://account/credits')
    def account_resource() -> dict:
        return get_account_resource(provider)

    @app.get('/healthz')
    def healthz() -> dict:
        health = HealthStatus(
            status='ok',
            provider=provider.name,
            database=db.ping(),
            redis=transient_store.ping(),
            tools={'count': registry.count, 'names': [tool.name for tool in registry.list_metadata()]},
            queue={'backend': settings.queue_backend, 'mode': 'inline'},
        )
        return health.model_dump(mode='json')

    @app.get('/tools')
    def list_tools_endpoint() -> dict:
        return {'tools': [tool.model_dump(mode='json') for tool in registry.list_metadata()]}

    @app.get('/jobs/{job_id}')
    def get_job(job_id: str) -> dict:
        record = job_service.get_job(job_id)
        if record is None:
            raise DigenError('JOB_NOT_FOUND', 'No job exists for the supplied job_id.', False)
        return record.model_dump(mode='json')

    @app.post('/jobs')
    def submit_jobs(submission: WorkflowSubmissionInput) -> dict:
        metrics.increment('workflow_requests_total')
        return workflow_service.execute(submission).model_dump(mode='json')

    @app.post('/tools/{tool_name}/invoke')
    def invoke_tool(tool_name: str, payload: dict | None = None) -> dict:
        return invoke(tool_name, payload)

    @app.get('/resources/models')
    def http_models() -> dict:
        return get_models_resource(provider)

    @app.get('/resources/tools')
    def http_tools() -> dict:
        return {'tools': [tool.model_dump(mode='json') for tool in registry.list_metadata()]}

    @app.get('/resources/limits')
    def http_limits() -> dict:
        return get_limits_resource()

    @app.get('/metrics', response_class=PlainTextResponse)
    def metrics_endpoint() -> str:
        return metrics.render()

    @app.websocket('/ws/jobs/{job_id}')
    async def job_updates(job_id: str, websocket: WebSocket) -> None:
        await notifier.connect(job_id, websocket)
        record = job_service.get_job(job_id)
        if record is not None:
            await websocket.send_json(record.model_dump(mode='json'))
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            notifier.disconnect(job_id, websocket)

    @app.exception_handler(DigenError)
    async def digen_error_handler(_, exc: DigenError):
        from fastapi.responses import JSONResponse
        status_code = 404 if exc.detail.code in {'JOB_NOT_FOUND', 'UNKNOWN_TOOL', 'UNKNOWN_DEPENDENCY'} else 400
        return JSONResponse(status_code=status_code, content=exc.to_envelope().model_dump(mode='json'))

    return Runtime(mcp=mcp, app=app, provider=provider, job_service=job_service, registry=registry, workflow_service=workflow_service, notifier=notifier)
