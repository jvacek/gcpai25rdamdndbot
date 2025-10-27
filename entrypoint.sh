#!/bin/sh

# Start the Node.js server (dnd-mcp) in the background
echo "Starting dnd-mcp Node.js server in background..."
cd /code/dnd-mcp

if [ -f "package.json" ]; then
    # Use nohup to detach the process and redirect stdout/stderr to /dev/null
    # The '&' runs it in the background
    nohup npm start > /dev/null 2>&1 &
else
    echo "No package.json found in /code/dnd-mcp, not starting Node.js server."
fi

# Go back to the Python app's directory
cd /code

# Start the Python (uvicorn) server in the foreground
# 'exec' replaces the shell with the uvicorn process,
# which is the correct way to run the main container command.
echo "Starting Python uvicorn server in foreground..."
exec uv run uvicorn app.server:app --host 0.0.0.0 --port 8080
