"""
Tool for getting dataset information (columns, types, row count, etc.).
"""

import json
from pathlib import Path

from ..core.enums import ResponseFormat
from ..models.input_models import GetDatasetInfoInput
from ..utils.dataset_readers import read_dataset_info


async def tealflow_get_dataset_info(params: GetDatasetInfoInput) -> str:
    """
    Get detailed information about a dataset file.

    This tool reads a dataset file (.rds or .csv) and returns metadata including:
    - Column names and data types
    - Row count
    - File size
    - Optional sample values for each column

    Args:
        params: Input parameters including file path, sample values flag, and response format

    Returns:
        Formatted string (markdown or JSON) with dataset information

    Raises:
        FileNotFoundError: If the dataset file doesn't exist
        ValueError: If the file format is not supported or file cannot be read
    """
    file_path = Path(params.file_path)

    # Validate that path is absolute
    if not file_path.is_absolute():
        raise ValueError(f"File path must be absolute, not relative. Received: {params.file_path}")

    # Read dataset information
    dataset_info = read_dataset_info(file_path, include_sample_values=params.include_sample_values)

    # Format output based on response format
    if params.response_format == ResponseFormat.MARKDOWN:
        return _format_markdown(file_path, dataset_info, params.include_sample_values)
    else:
        return _format_json(file_path, dataset_info)


def _format_markdown(file_path: Path, dataset_info, include_sample_values: bool) -> str:
    """Format dataset info as markdown."""
    lines = []

    lines.append("# Dataset Information")
    lines.append("")
    lines.append(f"**File**: `{file_path}`")
    lines.append(f"**Rows**: {dataset_info.row_count:,}")
    lines.append(f"**Columns**: {len(dataset_info.columns)}")
    lines.append(f"**File Size**: {_format_file_size(dataset_info.file_size_bytes)}")
    lines.append("")

    lines.append("## Columns")
    lines.append("")

    if include_sample_values:
        # Show detailed format with sample values
        for i, col in enumerate(dataset_info.columns, 1):
            lines.append(f"### {i}. {col.name}")
            lines.append(f"- **Type**: `{col.type}`")
            if col.sample_values:
                lines.append(
                    f"- **Sample Values**: {', '.join(f'`{v}`' for v in col.sample_values)}"
                )
            lines.append("")
    else:
        # Show compact table format
        lines.append("| # | Column Name | Type |")
        lines.append("|---|-------------|------|")
        for i, col in enumerate(dataset_info.columns, 1):
            lines.append(f"| {i} | `{col.name}` | `{col.type}` |")
        lines.append("")

    return "\n".join(lines)


def _format_json(file_path: Path, dataset_info) -> str:
    """Format dataset info as JSON."""
    output = {
        "file_path": str(file_path),
        "row_count": dataset_info.row_count,
        "column_count": len(dataset_info.columns),
        "file_size_bytes": dataset_info.file_size_bytes,
        "columns": [
            {
                "name": col.name,
                "type": col.type,
                "sample_values": col.sample_values,
            }
            for col in dataset_info.columns
        ],
    }
    return json.dumps(output, indent=2)


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
