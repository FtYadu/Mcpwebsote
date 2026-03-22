"""Entrypoint for the digen-mcp server."""

from __future__ import annotations

import argparse
from typing import Any

from fastapi import FastAPI

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

from app.config import get_settings
from app.logging_config import configure_logging
from app.resources.account_resource import get_account_resource
from app.resources.limits_resource import get_limits_resource
from app.resources.models_resource import get_models_resource
from app.resources.tools_resource import get_tools_resource
from app.services.job_service import JobService
from app.services.provider_router import ProviderRouter
from app.storage.db import SQLiteJobStore
from app.storage.redis_client import RedisBackedStateStore
from app.tools import (
    boost_fps,
    download_result,
    edit_image,
    generate_image,
    get_account_credits,
    get_job_status,
    image_to_video,
    list_models,
    list_tools,
    text_to_video,
    upscale_image,
    upscale_video,
)


def build_runtime() -> tuple[FastMCP, FastAPI, Any, JobService]:
    """Build MCP and HTTP app instances."""

    settings = get_settings()
    configure_logging(settings.log_level)
    router = ProviderRouter(settings)
    provider = router.provider
    db = SQLiteJobStore(settings.db_file)
    transient_store = RedisBackedStateStore(settings.redis_url)
    job_service = JobService(db, transient_store, provider.name)

    mcp = FastMCP('digen-mcp')
    app = FastAPI(title='digen-mcp-internal')

    generate_image.register(mcp, provider, job_service)
    edit_image.register(mcp, provider, job_service)
    text_to_video.register(mcp, provider, job_service)
    image_to_video.register(mcp, provider, job_service)
    upscale_image.register(mcp, provider, job_service)
    upscale_video.register(mcp, provider, job_service)
    boost_fps.register(mcp, provider, job_service)
    get_job_status.register(mcp, provider, job_service)
    download_result.register(mcp, provider, job_service)
    list_models.register(mcp, provider, job_service)
    list_tools.register(mcp, provider, job_service)
    get_account_credits.register(mcp, provider, job_service)

    @mcp.resource('digen://models')
    def models_resource() -> dict:
        return get_models_resource(provider)

    @mcp.resource('digen://tools')
    def tools_resource() -> dict:
        return get_tools_resource(provider)

    @mcp.resource('digen://limits/uploads')
    def limits_resource() -> dict:
        return get_limits_resource()

    @mcp.resource('digen://account/credits')
    def account_resource() -> dict:
        return get_account_resource(provider)

    @app.get('/healthz')
    def healthz() -> dict:
        return {'status': 'ok', 'provider': provider.name}

    @app.get('/resources/models')
    def http_models() -> dict:
        return get_models_resource(provider)

    @app.get('/resources/tools')
    def http_tools() -> dict:
        return get_tools_resource(provider)

    @app.get('/resources/limits')
    def http_limits() -> dict:
        return get_limits_resource()

    return mcp, app, provider, job_service


def main() -> None:
    """CLI entrypoint. Defaults to stdio MCP transport."""

    parser = argparse.ArgumentParser(description='Run digen-mcp')
    parser.add_argument('--http', action='store_true', help='Run the optional FastAPI wrapper instead of MCP stdio.')
    args = parser.parse_args()

    mcp, app, _, _ = build_runtime()
    if args.http:
        import uvicorn
        settings = get_settings()
        uvicorn.run(app, host=settings.http_host, port=settings.http_port)
        return
    mcp.run()


if __name__ == '__main__':
    main()
