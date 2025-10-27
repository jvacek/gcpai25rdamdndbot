import os
import pathlib

import google.auth
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

# Define the path to your D&D MCP server
# IMPORTANT: This MUST be an ABSOLUTE path to your D&D MCP server directory
DND_MCP_SERVER_PATH = os.environ.get(
    "DND_MCP_SERVER_PATH",
    pathlib.Path(__file__).parent.parent.parent.parent / "dnd-mcp",
)

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="dnd_rules_agent",
    instruction="""
    You are a helpful D&D 5e assistant and rules expert. Use the available MCP tools to help users with:
    - Character creation and management
    - Spell lookups and information
    - Equipment and item details
    - Rule clarifications
    - Combat mechanics

    Always be helpful and provide accurate D&D 5e information using the tools available to you.
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="node",
                    args=["dist/index.js"],
                    cwd=DND_MCP_SERVER_PATH,
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # Uncomment and customize as needed:
            # tool_filter=['spell_lookup', 'character_info', 'equipment_stats']
        )
    ],
)
