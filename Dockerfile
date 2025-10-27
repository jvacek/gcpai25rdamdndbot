# Start from the original Python image
FROM python:3.12-slim

# Install system dependencies: git for cloning, nodejs & npm for the node app
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN pip install --no-cache-dir uv==0.9.5

WORKDIR /code

# --- Clone and build the dnd-mcp repository ---
RUN git clone https://github.com/heffrey78/dnd-mcp.git /tmp/dnd-mcp && \
    cd /tmp/dnd-mcp && \
    npm install && \
    npm run build

# Copy Python application files
COPY ./pyproject.toml ./README.md ./uv.lock* ./
COPY ./app ./app

# Sync Python dependencies
RUN uv sync --frozen

# --- Environment variables ---
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

# Point DND_MCP_SERVER_PATH to the built JS file
ENV DND_MCP_SERVER_PATH="/tmp/dnd-mcp"

EXPOSE 8080

# --- Run the server ---
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]
