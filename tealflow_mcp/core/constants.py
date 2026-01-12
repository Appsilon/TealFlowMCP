"""
Constants and configuration for Teal Flow MCP Server.
"""

from pathlib import Path

# Workspace is at flow/workspace/, MCP is at flow/mcp/server/tealflow_mcp/core/
WORKSPACE_DIR = Path(__file__).parent.parent.parent / "workspace"

# Maximum response size in characters
CHARACTER_LIMIT = 25000
