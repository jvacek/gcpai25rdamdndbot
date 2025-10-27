# Stage 1: Build the Node.js application
FROM node:22 AS node-builder

# Clone and build the dnd-mcp repository
RUN git clone https://github.com/heffrey78/dnd-mcp.git /tmp/dnd-mcp
WORKDIR /tmp/dnd-mcp
RUN npm install && npm run build

# Stage 2: Main Python application
FROM python:3.12-slim

# Install system dependencies (no longer need nodejs/npm)

# Install uv (Python package manager)
RUN pip install --no-cache-dir uv==0.9.5

WORKDIR /code

# Copy the built Node.js application from the builder stage
COPY --from=node-builder /tmp/dnd-mcp /tmp/dnd-mcp

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
ENV GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-00-f40a98878280"

EXPOSE 8080

# --- Run the server ---
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]
