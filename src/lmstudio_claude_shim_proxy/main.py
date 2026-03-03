"""
LM Studio proxy for Claude Code.

Fixes:
  - Patches tool input_schema to add missing 'properties: {}' which LM Studio
    requires but Anthropic's own API does not enforce.

Optional:
  - Injects speculative decoding config when DRAFT_MODEL is set.
"""

import json
import logging
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

LMSTUDIO_URL = os.environ.get("LMSTUDIO_URL", "http://host.docker.internal:1234")
DRAFT_MODEL   = os.environ.get("DRAFT_MODEL", "").strip()

# ---------------------------------------------------------------------------
# LM Studio speculative decoding field name.
#
# On the OpenAI-compatible endpoint LM Studio uses:
#   "lmstudio_speculative_decoding": { "draft_model": "<name>" }
#
# On the Anthropic-compatible endpoint the field name is not confirmed in
# public docs — this is the best known equivalent. If LM Studio uses a
# different key on /v1/messages you can override via:
#   SPEC_FIELD=some_other_field docker compose up
# and check /_health to confirm what's being injected.
# ---------------------------------------------------------------------------
SPEC_FIELD = os.environ.get("SPEC_FIELD", "lmstudio_speculative_decoding")


app = FastAPI(title="LM Studio Claude Code Proxy")


def patch_tools(data: dict) -> int:
    """Add properties:{} to any tool input_schema that is missing it.
    Returns the number of tools patched."""
    patched = 0
    for i, tool in enumerate(data.get("tools", [])):
        schema = tool.get("input_schema", {})
        if schema.get("type") == "object" and "properties" not in schema:
            schema["properties"] = {}
            log.debug("Patched tool[%d] '%s': added properties:{}", i, tool.get("name"))
            patched += 1
    return patched


def inject_speculative_decoding(data: dict) -> bool:
    """Inject speculative decoding config if DRAFT_MODEL is configured.
    Returns True if injected."""
    if not DRAFT_MODEL:
        return False
    if SPEC_FIELD in data:
        return False  # already present, don't overwrite
    data[SPEC_FIELD] = {"draft_model": DRAFT_MODEL}
    return True

@app.get("/_health")
async def health():
    return {
        "status": "ok",
        "upstream": LMSTUDIO_URL,
        "speculative_decoding": {
            "enabled": bool(DRAFT_MODEL),
            "draft_model": DRAFT_MODEL or None,
            "field_name": SPEC_FIELD,
        },
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    body = await request.body()

    if body:
        try:
            data = json.loads(body)

            patched = patch_tools(data)
            if patched:
                log.info("Patched %d tool schema(s) on /%s", patched, path)

            if inject_speculative_decoding(data):
                log.info(
                    "Injected speculative decoding: %s -> draft_model=%s",
                    SPEC_FIELD, DRAFT_MODEL,
                )

            body = json.dumps(data).encode()
        except (json.JSONDecodeError, AttributeError):
            pass  # non-JSON body, pass through unchanged

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

    target_url = f"{LMSTUDIO_URL}/{path}"

    async def stream_response():
        async with httpx.AsyncClient(timeout=600) as client:
            async with client.stream(
                request.method,
                target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            ) as resp:
                async for chunk in resp.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        stream_response(),
        status_code=200,
        media_type="text/event-stream",
    )

