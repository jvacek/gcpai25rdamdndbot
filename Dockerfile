FROM python:3.12-slim

# Install system dependencies (git, curl, node)
RUN apt-get update && apt-get install -y curl git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install uv (Python project manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.cargo/bin/uv /usr/local/bin/uv

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
ENV DND_MCP_SERVER_PATH="/tmp/dnd-mcp/dist/index.js"

EXPOSE 8080

# --- Run the server ---
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]
