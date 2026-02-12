# Claude to LM Studio Shim Proxy

A lightweight proxy service that bridges Claude API requests to a local LM Studio instance.

## Features

- FastAPI-based proxy server
- Forwards Claude `/v1/messages` requests to LM Studio `/v1/chat/completions`
- Optional authentication token support
- Health check endpoint
- Containerized with Docker

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
python -m uvicorn src.main:app --reload
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
  -e LM_STUDIO_URL=http://host.docker.internal:1234 \
  lmstudio-claude-shim-proxy
```

### Configuration

Environment variables:

- `LM_STUDIO_URL` - LM Studio API base URL (default: `http://localhost:1234`)
- `CLAUDE_PROXY_AUTH_TOKEN` - Optional authentication token for requests

## API Endpoints

### Health Check

```
GET /health
```

Returns `{"status": "healthy", "service": "claude-shim-proxy"}`

### Claude Messages Proxy

```
POST /v1/messages
Authorization: Bearer <token>

{
  "model": "...",
  "messages": [...],
  ...
}
```

Forwards to LM Studio's `/v1/chat/completions` endpoint.

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
│   └── main.py           # Main application
├── tests/                # Test directory
├── pyproject.toml        # Project configuration & dependencies
├── Dockerfile            # Docker image definition
└── README.md
```
