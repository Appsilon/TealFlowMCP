"""
Dataset discovery tool for TealFlow MCP Server.

This module provides MCP tool wrappers for discovering ADaM datasets.
"""

from ..core.enums import ResponseFormat
from ..models.input_models import DiscoverDatasetsInput
from .discovery import discover_datasets


async def tealflow_discover_datasets(params: DiscoverDatasetsInput) -> str:
    """
    Discover ADaM datasets in a directory.

    This tool scans a directory for ADaM dataset files, identifies the dataset
    names, and collects metadata about each dataset.

    Args:
        params: Input parameters including:
            - data_directory: Path to the directory containing dataset files
            - file_formats: Optional list of file formats to include
            - pattern: File pattern to match
            - response_format: Output format (markdown or json)

    Returns:
        str: Discovery results in the requested format
    """
    # Call the discovery function
    result = discover_datasets(
        data_directory=params.data_directory,
        file_formats=params.file_formats,
        pattern=params.pattern,
    )

    # Format the response
    if params.response_format == ResponseFormat.JSON:
        import json

        return json.dumps(result, indent=2)
    else:
        # Format as markdown
        return _format_discovery_markdown(result)


def _format_discovery_markdown(result: dict) -> str:
    """
    Format discovery results as markdown.

    Args:
        result: Discovery results dictionary

    Returns:
        str: Formatted markdown string
    """
    lines = []

    # Header
    lines.append("# ADaM Dataset Discovery Results")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- **Directory:** `{result['data_directory']}`")
    lines.append(f"- **Datasets Found:** {result['count']}")
    lines.append(f"- **Supported Formats:** {', '.join(result['supported_formats'])}")
    lines.append("")

    # Datasets table
    if result["count"] > 0:
        lines.append("## Discovered Datasets")
        lines.append("")
        lines.append("| Dataset | Format | Standard | Size | Path |")
        lines.append("|---------|--------|----------|------|------|")

        for dataset in result["datasets_found"]:
            name = dataset["name"]
            fmt = dataset["format"]
            is_standard = "✓" if dataset["is_standard_adam"] else "Custom"
            size_kb = dataset["size_bytes"] / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb > 0 else "0 B"
            path = dataset["path"]

            lines.append(f"| {name} | {fmt} | {is_standard} | {size_str} | `{path}` |")

        lines.append("")
    else:
        lines.append("## No Datasets Found")
        lines.append("")
        lines.append("No ADaM datasets were found in the specified directory.")
        lines.append("")

    # Warnings
    if result["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for warning in result["warnings"]:
            lines.append(f"- ⚠️  {warning}")
        lines.append("")

    return "\n".join(lines)
