# Claude to LM Studio Shim Proxy

A proxy server that bridges Anthropic's Claude API to a local LM Studio instance. Handles API compatibility fixes and optional speculative decoding.

## Features

- **API Compatibility**: Automatically patches tool schemas to add missing `properties: {}` for LM Studio compatibility
- **Full Path Proxy**: Proxies all HTTP methods (GET, POST, PUT, DELETE, PATCH) to any endpoint
- **Streaming Support**: Preserves streaming responses for real-time output
- **Speculative Decoding**: Optional draft model injection for faster inference
- **Health Check**: Detailed health endpoint showing configuration
- **FastAPI-based**: Modern async Python web framework

## What It Fixes

LM Studio requires tool input schemas to have a `properties` field, while Anthropic's API does not enforce this. This proxy automatically patches the request to ensure compatibility.

### Example: Tool Schema Patching

**Input:**
```json
{
  "tools": [{
    "name": "example_tool",
    "input_schema": {
      "type": "object"
    }
  }]
}
```

**Output (patched):**
```json
{
  "tools": [{
    "name": "example_tool",
    "input_schema": {
      "type": "object",
      "properties": {}
    }
  }]
}
```

## Quick Start

### Local Development

**Prerequisites:**
- Python 3.11+
- `uv` package manager

**Installation:**

```bash
# Install dependencies
uv pip install -r pyproject.toml

# Run the proxy
python -m uvicorn lmstudio_claude_shim_proxy.main:app --reload
```

The proxy will be available at `http://localhost:8000`

### Docker

**Build the image:**

```bash
docker build -t lmstudio-claude-shim-proxy .
```

**Run the container:**

```bash
docker run -p 8000:8000 \
  -e LMSTUDIO_URL=http://host.docker.internal:1234 \
  lmstudio-claude-shim-proxy
```

**With speculative decoding:**

```bash
docker run -p 8000:8000 \
  -e LMSTUDIO_URL=http://host.docker.internal:1234 \
  -e DRAFT_MODEL=llama-2-7b-chat \
  lmstudio-claude-shim-proxy
```

### Docker Compose

```bash
# With default settings
docker-compose up

# With draft model for speculative decoding
DRAFT_MODEL=llama-2-7b-chat docker-compose up
```

## Configuration

Environment variables:

- `LMSTUDIO_URL` - LM Studio API base URL (default: `http://host.docker.internal:1234`)
- `DRAFT_MODEL` - Optional draft model name for speculative decoding
- `SPEC_FIELD` - Speculative decoding field name (default: `lmstudio_speculative_decoding`)

## API Endpoints

### Health Check

```
GET /_health
```

Returns health status and configuration:

```json
{
  "status": "ok",
  "upstream": "http://host.docker.internal:1234",
  "speculative_decoding": {
    "enabled": false,
    "draft_model": null,
    "field_name": "lmstudio_speculative_decoding"
  }
}
```

### Proxy (All Routes)

```
GET|POST|PUT|DELETE|PATCH /{path}
```

Proxies all requests to the configured LM Studio URL. Automatically patches tool schemas and optionally injects speculative decoding config.

## Development

**Run tests:**

```bash
uv run pytest
```

**Format code:**

```bash
uv run black src tests
uv run ruff check --fix src tests
```

**Type checking:**

```bash
uv run mypy src
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   └── main.py                    # Main proxy application
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml                 # Project configuration & dependencies
├── requirements.txt               # Compiled dependencies
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker Compose configuration
├── .dockerignore
├── .gitignore
└── README.md
```

## Troubleshooting

**Check proxy is working:**
```bash
curl http://localhost:8000/_health
```

**View logs with Docker Compose:**
```bash
docker-compose logs -f proxy
```

**Verify tool patching:**
Enable debug logging by setting `logging.basicConfig(level=logging.DEBUG)` in `main.py`

## License

MIT
