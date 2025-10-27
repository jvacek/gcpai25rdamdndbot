# Start from the original Python image
FROM python:3.11-slim

# Install system dependencies: git for cloning, nodejs & npm for the node app
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN pip install --no-cache-dir uv==0.8.13

# Set up the main Python application
WORKDIR /code
COPY ./pyproject.toml ./README.md ./uv.lock* ./
COPY ./app ./app
RUN uv sync --frozen

# --- Set up the Node.js (dnd-mcp) application ---

# Add an argument for the repository URL.
ARG DND_MCP_REPO_URL="https://github.com/heffrey78/dnd-mcp.git"

# Clone, install, and build the Node.js app
# We check if the URL is provided, otherwise skip cloning
RUN if [ -n "$DND_MCP_REPO_URL" ]; then \
        git clone ${DND_MCP_REPO_URL} dnd-mcp; \
    else \
        echo "DND_MCP_REPO_URL not provided, skipping clone. Creating empty dir."; \
        mkdir dnd-mcp; \
    fi

WORKDIR /code/dnd-mcp
RUN if [ -f "package.json" ]; then \
        npm install && npm run build; \
    else \
        echo "No package.json found, skipping npm install/build."; \
    fi

# Go back to the main Python app directory
WORKDIR /code

# --- Original Python App Config ---
ARG COMMIT_SHA=""
ENV COMMIT_SHA=${COMMIT_SHA}

# Set the DND_MCP_SERVER_PATH to the directory where we cloned the repo
ARG DND_MCP_SERVER_PATH="/code/dnd-mcp"
ENV DND_MCP_SERVER_PATH=${DND_MCP_SERVER_PATH}

EXPOSE 8080

# Copy the entrypoint script that will launch both servers
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Run the entrypoint script
CMD ["./entrypoint.sh"]
