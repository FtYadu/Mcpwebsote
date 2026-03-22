# digen-mcp

`digen-mcp` is a production-oriented MCP server for Digen-style AI creative workflows. It exposes typed MCP tools for image generation, image editing, text-to-video, image-to-video, upscaling, FPS boosting, job polling, result downloads, model discovery, tool discovery, and account credit lookup.

## Supported tools

- `generate_image`
- `edit_image`
- `text_to_video`
- `image_to_video`
- `upscale_image`
- `upscale_video`
- `boost_fps`
- `get_job_status`
- `download_result`
- `list_models`
- `list_tools`
- `get_account_credits`

## Excluded features

This project intentionally does **not** implement:

- watermark removal
- DRM bypass
- tools that remove ownership marks or copyright identifiers
- account scraping outside authenticated, user-owned access

Those features are excluded for security, compliance, and platform-integrity reasons.

## Architecture

- **FastMCP** for MCP tool and resource registration
- **Pydantic v2** for schemas
- **FastAPI** for optional internal HTTP health/introspection endpoints
- **Provider abstraction** with `MockProvider`, `APIProvider`, and scaffolded `PlaywrightProvider`
- **SQLite** for local persistence
- **Redis** for transient job state when available, with in-memory fallback otherwise

## Resources

- `digen://models`
- `digen://tools`
- `digen://limits/uploads`
- `digen://account/credits`

## Local setup

```bash
cp .env.example .env
make install
```

## Run locally

By default the server uses stdio-friendly MCP wiring with the mock provider:

```bash
make run
```

You can also run the optional FastAPI wrapper app:

```bash
cd digen-mcp
python -m app.main --http
```

## Provider configuration

### MockProvider

Set:

```env
DIGEN_PROVIDER=mock
```

This provider is deterministic and intended for local development and tests.

### APIProvider

Set:

```env
DIGEN_PROVIDER=api
DIGEN_API_BASE_URL=https://api.example.com
DIGEN_API_TOKEN=your-token
```

`APIProvider` is production-oriented but only calls explicitly configured endpoints. It does not invent undocumented Digen endpoints.

### PlaywrightProvider

Set:

```env
DIGEN_PROVIDER=playwright
DIGEN_PLAYWRIGHT_BASE_URL=https://example.com
DIGEN_PLAYWRIGHT_USERNAME=you@example.com
DIGEN_PLAYWRIGHT_PASSWORD=secret
```

This provider is a fallback scaffold only. It contains login/session hook points and clearly marked TODO regions instead of brittle scraping logic.

## MCP stdio client example

Example client configuration:

```json
{
  "mcpServers": {
    "digen-mcp": {
      "command": "python",
      "args": ["-m", "app.main"],
      "cwd": "/absolute/path/to/digen-mcp",
      "env": {
        "DIGEN_PROVIDER": "mock"
      }
    }
  }
}
```

## Example requests and responses

### `generate_image`

Request:

```json
{
  "prompt": "cinematic neon tiger portrait",
  "model": "mock-image-v1",
  "aspect_ratio": "1:1",
  "reference_images": ["https://example.com/ref.png"]
}
```

Response:

```json
{
  "job_id": "job-generate_image-0001",
  "status": "queued",
  "model": "mock-image-v1",
  "preview_url": "https://mock.digen.local/previews/job-generate_image-0001.jpg",
  "result_url": null
}
```

### `get_job_status`

Response:

```json
{
  "job_id": "job-generate_image-0001",
  "status": "processing",
  "progress": 50,
  "stage": "rendering",
  "preview_url": "https://mock.digen.local/previews/job-generate_image-0001.jpg",
  "result_url": null,
  "error": null
}
```

## Upload limits resource

`digen://limits/uploads` publishes readable text and structured JSON for:

- image upscaler: JPG/JPEG/PNG/WEBP up to 10 MB
- video upscaler: MP4/MOV/AVI/WEBM up to 30 MB
- FPS booster: MP4 up to 30 MB

## Tests

```bash
make test
```

The test suite covers schema validation, provider routing, mock job lifecycle, and resource handlers.
