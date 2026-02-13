"""
Prompt generation functions for TealFlow MCP Server.
"""

from ..core.constants import KNOWLEDGE_BASE_DIR


async def tealflow_get_agent_guidance() -> str:
    """Read and return the agent guidance document."""
    agent_md_path = KNOWLEDGE_BASE_DIR / "agent.md"

    if not agent_md_path.exists():
        return "Error: Agent guidance document not found."

    with open(agent_md_path, encoding="utf-8") as f:
        content = f.read()

    return content
