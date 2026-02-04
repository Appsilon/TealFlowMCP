"""
Formatting utilities for Teal Flow MCP Server.
"""

import json
from typing import Any

from ..core.constants import CHARACTER_LIMIT


def _format_module_list_markdown(modules: dict[str, Any], package: str) -> str:
    """Format module list as markdown."""
    lines = [f"# Teal Modules ({package.title()})", ""]

    for module_name, module_info in sorted(modules.items()):
        lines.append(f"## {module_name}")
        lines.append(f"**Description**: {module_info.get('description', 'N/A')}")

        datasets = module_info.get("required_datasets", [])
        if datasets:
            lines.append(f"**Required Datasets**: {', '.join(datasets)}")
        else:
            lines.append("**Required Datasets**: None (works with any data.frame)")

        lines.append("")

    return "\n".join(lines)


def _format_module_list_json(modules: dict[str, Any]) -> str:
    """Format module list as JSON."""
    module_list = []
    for module_name, module_info in sorted(modules.items()):
        module_list.append(
            {
                "name": module_name,
                "description": module_info.get("description", ""),
                "required_datasets": module_info.get("required_datasets", []),
            }
        )

    return json.dumps({"modules": module_list, "count": len(module_list)}, indent=2)


def _truncate_response(
    response: str, message: str = "Response truncated. Use filters to reduce results."
) -> str:
    """Truncate response if it exceeds CHARACTER_LIMIT."""
    if len(response) <= CHARACTER_LIMIT:
        return response

    truncated = response[: CHARACTER_LIMIT - len(message) - 10]
    return f"{truncated}\n\n... {message}"
