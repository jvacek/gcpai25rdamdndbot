# Stage 1: Build the Node.js application
FROM node:22 AS prod

WORKDIR /code

# Clone and build the dnd-mcp repository
COPY ./dnd-mcp ./dnd-mcp

RUN cd dnd-mcp && npm install && npm run build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy Python requirements
COPY ./pyproject.toml ./uv.lock* ./

# Sync Python dependencies
RUN uv sync --frozen

# Copy the rest of the app
COPY ./app ./app

# --- Environment variables ---
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

# Point DND_MCP_SERVER_PATH to the built JS file
# ENV DND_MCP_SERVER_PATH="/tmp/dnd-mcp"
ENV GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-00-f40a98878280"

EXPOSE 8080

# --- Run the server ---
CMD ["uv", "run", "uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]
