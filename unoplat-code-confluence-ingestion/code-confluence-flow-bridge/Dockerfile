# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager and ruff
RUN pip install --no-cache-dir uv
RUN pip install --no-cache-dir ruff

# Set working directory
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync
RUN uv sync --frozen --no-cache

# Copy the rest of the application files
COPY . /app/

# Expose the port that the FastAPI app listens on
EXPOSE 8000

# Use exec form for proper signal handling
CMD ["uv", "run", "uvicorn", "src.code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"] 