"""
Data loading code generation tool for TealFlow MCP Server.

This module provides functionality for generating R code that loads ADaM datasets
and creates teal_data objects.
"""

from typing import Any

from ..models.input_models import GenerateDataLoadingInput
from ..core.enums import ResponseFormat
from .format_handlers import get_format_handler_by_name


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
    # Validate input
    if not datasets:
        raise ValueError("No datasets provided. At least one dataset is required.")

    lines = []

    # Library import
    lines.append("library(teal)")
    lines.append("")

    # Sort datasets alphabetically by name for consistent output
    sorted_datasets = sorted(datasets, key=lambda d: d["name"])

    dataset_names = []
    has_non_standard = False

    # Generate loading code for each dataset
    for dataset in sorted_datasets:
        name = dataset["name"]
        path = dataset["path"]
        format_type = dataset["format"]
        is_standard = dataset["is_standard_adam"]

        dataset_names.append(name)

        if not is_standard:
            has_non_standard = True

        # Get appropriate format handler and generate loading code
        handler = get_format_handler_by_name(format_type)
        if handler:
            loading_code = handler.get_loading_code(name, path)
            lines.append(loading_code)
        else:
            # Fallback for unknown formats (shouldn't happen with validated input)
            lines.append(f'# WARNING: Unknown format "{format_type}" for {name}')
            lines.append(f'# {name} <- load_data("{path}")  # Implement manually')

    lines.append("")
    lines.append("## Data reproducible code ----")

    # Generate teal_data() call
    lines.append("data <- teal_data(")

    # Add dataset assignments
    for name in dataset_names:
        lines.append(f"  {name} = {name},")

    # Add join keys section
    if has_non_standard:
        lines.append("  # WARNING: Non-standard datasets detected.")
        lines.append("  # You may need to configure join_keys manually.")
        lines.append("  # join_keys = ...")
    else:
        # Use default CDISC join keys for standard datasets
        dataset_names_str = '", "'.join(dataset_names)
        lines.append(f'  join_keys = default_cdisc_join_keys[c("{dataset_names_str}")]')

    lines.append(")")
    lines.append("")

    return "\n".join(lines)


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
    try:
        # Generate the R code
        code = generate_data_loading_code(params.datasets)

        # Format response based on requested format
        if params.response_format == ResponseFormat.JSON:
            import json

            dataset_names = [ds["name"] for ds in params.datasets]
            return json.dumps(
                {
                    "code": code,
                    "datasets": dataset_names,
                    "file_path": "data/data.R",
                    "instructions": [
                        "Create a 'data/' directory in your project if it doesn't exist",
                        "Save the code as 'data/data.R'",
                        "The app template will load this with source('data/data.R')",
                    ],
                },
                indent=2,
            )
        else:
            # Markdown format
            return _format_data_loading_markdown(code, params.datasets)

    except Exception as e:
        return f"Error generating data loading code: {e!s}"


def _format_data_loading_markdown(code: str, datasets: list[dict[str, Any]]) -> str:
    """
    Format data loading code as markdown.

    Args:
        code: The generated R code
        datasets: List of dataset dictionaries

    Returns:
        str: Markdown formatted response with code and usage instructions
    """
    lines = []

    lines.append("# Data Loading Code")
    lines.append("")
    lines.append("Save this code as `data/data.R` in your project:")
    lines.append("")
    lines.append("```r")
    lines.append(code)
    lines.append("```")
    lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append("1. Create a `data/` directory in your project if it doesn't exist")
    lines.append("2. Save the code above as `data/data.R`")
    lines.append("3. The app template will load this with `source(\"data/data.R\")`")
    lines.append("")

    lines.append("## Datasets Included")
    lines.append("")
    for dataset in sorted(datasets, key=lambda d: d["name"]):
        name = dataset["name"]
        format_type = dataset.get("format", "unknown")
        lines.append(f"- **{name}** ({format_type})")
    lines.append("")

    return "\n".join(lines)
