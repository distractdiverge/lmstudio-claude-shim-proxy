FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .

# Install dependencies with uv
RUN uv pip install --system -r <(uv pip compile pyproject.toml)

# Copy application code
COPY src/ src/

# Expose the default port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "lmstudio_claude_shim_proxy.main:app", "--host", "0.0.0.0", "--port", "8000"]
