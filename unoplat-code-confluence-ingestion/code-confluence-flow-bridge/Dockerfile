# Minimal Python 3.12 Web image (slim variant)
FROM python:3.12-slim

# Install Java and Git
RUN apt-get update && \
    apt-get install -y wget gnupg curl git && \
    curl -s https://repos.azul.com/azul-repo.key | gpg --dearmor -o /usr/share/keyrings/azul.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" | \
    tee /etc/apt/sources.list.d/zulu.list && \
    apt-get update && \
    apt-get install -y zulu11-jre && \
    rm -rf /var/lib/apt/lists/*
# Set the JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/zulu11
# Install uv directly from the official image
RUN pip install uv
RUN pip install ruff
# Set working directory
WORKDIR /app

# Create directory for JAR file and copy it
RUN mkdir -p jars

# Copy the application files (including pyproject.toml)
COPY . /app/

# Install dependencies using uv sync
RUN uv sync --frozen --no-cache

# Expose the port that the FastAPI app listens on
EXPOSE 8000

# Start the FastAPI application
CMD ["uv", "run", "uvicorn", "src.code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"] 