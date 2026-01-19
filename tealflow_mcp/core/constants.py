"""
Constants and configuration for Teal Flow MCP Server.
"""

from pathlib import Path

# Knowledge base directory containing datasets and module metadata
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent / "knowledge_base"

# Maximum response size in characters
CHARACTER_LIMIT = 25000
