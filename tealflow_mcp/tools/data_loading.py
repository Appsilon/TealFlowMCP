"""
Data loading code generation tool for TealFlow MCP Server.

This module provides functionality for generating R code that loads ADaM datasets
and creates teal_data objects.
"""

from typing import Any

from ..models.input_models import GenerateDataLoadingInput
from ..core.enums import ResponseFormat


def generate_data_loading_code(datasets: list[dict[str, Any]]) -> str:
    """
    Generate R code for loading ADaM datasets and creating teal_data object.

    This function creates complete R code that:
    - Loads individual dataset files (.Rds or .csv)
    - Creates a teal_data object with proper join keys
    - Handles both standard and non-standard ADaM datasets

    Args:
        datasets: List of dataset dictionaries with keys:
            - name: Dataset name (e.g., "ADSL")
            - path: Absolute path to dataset file
            - format: File format ("Rds" or "csv")
            - is_standard_adam: Whether it's a standard ADaM dataset

    Returns:
        str: Complete R code for data loading

    Raises:
        ValueError: If datasets list is empty

    Example:
        >>> datasets = [
        ...     {
        ...         "name": "ADSL",
        ...         "path": "/data/ADSL.Rds",
        ...         "format": "Rds",
        ...         "is_standard_adam": True
        ...     }
        ... ]
        >>> code = generate_data_loading_code(datasets)
        >>> print(code)
        library(teal)

        ADSL <- readRDS("/data/ADSL.Rds")
        ...
    """
    pass


async def tealflow_generate_data_loading(params: GenerateDataLoadingInput) -> str:
    """
    MCP tool wrapper for generating data loading code.

    This tool generates R code for loading discovered ADaM datasets and creating
    a teal_data object. It's designed to work seamlessly with the output from
    tealflow_discover_datasets.

    Args:
        params: Input parameters including:
            - datasets: List of dataset dictionaries from discovery
            - response_format: Output format (markdown or json)

    Returns:
        str: Generated code in the requested format (markdown or JSON)

    Example Usage:
        After discovering datasets with tealflow_discover_datasets, pass the
        datasets_found array to this tool:

        ```python
        discovery_result = discover_datasets("/path/to/data")
        params = GenerateDataLoadingInput(
            datasets=discovery_result["datasets_found"]
        )
        code = await tealflow_generate_data_loading(params)
        ```
    """
    pass


def _format_data_loading_markdown(code: str, datasets: list[dict[str, Any]]) -> str:
    """
    Format data loading code as markdown.

    Args:
        code: The generated R code
        datasets: List of dataset dictionaries

    Returns:
        str: Markdown formatted response with code and usage instructions
    """
    pass
