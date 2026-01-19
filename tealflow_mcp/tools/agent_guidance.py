"""
Prompt generation functions for TealFlow MCP Server.
"""

from pathlib import Path


async def tealflow_get_agent_guidance() -> str:
    """Read and return the agent guidance document."""
    agent_md_path = Path(__file__).parent.parent.parent / "knowledge_base" / "agent.md"
    
    if not agent_md_path.exists():
        return "Error: Agent guidance document not found."
    
    with open(agent_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content
