# digen-mcp

`digen-mcp` is an MCP server for AI agents that need discoverable tools, typed execution contracts, chained workflows, and production-friendly operational endpoints.

## Project Overview

### Highlights
- Plugin-style `ToolRegistry` for dynamic tool discovery and consistent metadata.
- MCP and HTTP interfaces backed by the same execution layer.
- Batch workflow execution with task dependencies and parameter references.
- Realtime job notifications over WebSocket.
- Local utility tools for text analysis, document normalization, and speech-oriented workflows.
- SQLite for local development and PostgreSQL support for higher-concurrency deployments.
- Redis-backed transient state with automatic in-memory fallback.

### Built-in tool families
- **Creative provider tools**: image generation/editing, text-to-video, image-to-video, upscaling, FPS boosting.
- **Job tools**: job lookup, download resolution, provider models, provider tools, account credits.
- **Agent utility tools**: `summarize_text`, `analyze_sentiment`, `document_to_text`, `text_to_speech`, `transcribe_audio`.

## Installation Guide

### Local Python setup
```bash
cd digen-mcp
./scripts/bootstrap_env.sh
python -m pip install -r requirements.txt
python -m app.main --http
```

### Docker Compose setup
```bash
cd digen-mcp
./scripts/bootstrap_env.sh
# optionally set DIGEN_DATABASE_URL=postgresql://digen:digen@postgres:5432/digen in .env
docker compose up --build
```

### Key environment variables
- `DIGEN_PROVIDER`: `mock`, `api`, or `playwright`.
- `DIGEN_DATABASE_URL`: PostgreSQL DSN for production deployments.
- `DIGEN_DB_PATH`: SQLite file path when PostgreSQL is not used.
- `DIGEN_REDIS_URL`: Redis URL for transient state.
- `DIGEN_PUBLIC_BASE_URL`: Base URL used in generated artifact links.

## API Documentation

### Health and discovery
#### `GET /healthz`
Returns provider, database, Redis, queue mode, and registered tool inventory.

#### `GET /tools`
Returns all available tools with categories, tags, and input schemas for agent-side dynamic registration.

Example:
```http
GET /tools
```

### Single tool execution
#### `POST /tools/{tool_name}/invoke`
```http
POST /tools/summarize_text/invoke
Content-Type: application/json

{
  "text": "Fast, observable workflows help agents recover from partial failures.",
  "max_sentences": 1
}
```

### Batch and chained workflows
#### `POST /jobs`
Supports dependent task execution and parameter references via `$tasks.<id>.<field>`.

```http
POST /jobs
Content-Type: application/json

{
  "tasks": [
    {
      "id": 1,
      "tool": "generate_image",
      "parameters": {
        "prompt": "futuristic city skyline at dusk",
        "model": "mock-image-v1"
      }
    },
    {
      "id": 2,
      "tool": "get_job_status",
      "depends_on": [1],
      "parameters": {
        "job_id": "$tasks.1.job_id"
      }
    }
  ]
}
```

### WebSocket notifications
#### `GET ws://<host>/ws/jobs/{job_id}`
Subscribe to queued, processing, and completed job-state updates.

## Extending the MCP framework

1. Add or reuse a Pydantic input model in `app/models/tool_inputs.py`.
2. Implement execution logic in a provider or a local service.
3. Register the tool in `app/runtime/tool_registry.py` with metadata tags and category.
4. The tool automatically appears in `/tools` and becomes callable by the workflow engine.

## Architecture diagram
See [`docs/architecture.md`](docs/architecture.md).

## Developer Workflow

### Quality checks
```bash
make lint
make test
```

### CI/CD
GitHub Actions runs Ruff and pytest on every push and pull request.

### Monitoring
- `/metrics` exposes Prometheus-style counters.
- `/healthz` exposes dependency-level health.
- `/ws/jobs/{job_id}` streams lifecycle changes.

## License
This project is released under the MIT License. See [`LICENSE`](LICENSE).
