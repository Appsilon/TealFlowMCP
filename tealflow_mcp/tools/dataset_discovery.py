"""
Dataset discovery tool for TealFlow MCP Server.

This module provides MCP tool wrappers for discovering ADaM datasets.
"""

from ..models.input_models import DiscoverDatasetsInput
from ..core.enums import ResponseFormat
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
        pattern=params.pattern
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
    pass
