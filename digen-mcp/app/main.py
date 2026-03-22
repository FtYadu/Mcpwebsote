"""Entrypoint for the digen-mcp server."""

from __future__ import annotations

import argparse

from app.config import get_settings
from app.runtime.runtime import build_runtime


def main() -> None:
    """CLI entrypoint. Defaults to stdio MCP transport."""

    parser = argparse.ArgumentParser(description='Run digen-mcp')
    parser.add_argument('--http', action='store_true', help='Run the optional FastAPI wrapper instead of MCP stdio.')
    args = parser.parse_args()

    settings = get_settings()
    runtime = build_runtime(settings)
    if args.http:
        import uvicorn
        uvicorn.run(runtime.app, host=settings.http_host, port=settings.http_port)
        return
    runtime.mcp.run()


if __name__ == '__main__':
    main()
