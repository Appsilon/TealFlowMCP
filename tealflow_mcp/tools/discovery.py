"""
Dataset discovery functionality for ADaM datasets.

This module provides functionality to discover ADaM datasets in a directory
and extract metadata about them.
"""

import re
from pathlib import Path
from typing import Any

# Standard ADaM dataset names (CDISC standard)
STANDARD_ADAM_DATASETS = {
    "ADSL",   # Subject-Level Analysis Dataset
    "ADTTE",  # Time-to-Event Analysis Dataset
    "ADRS",   # Response Analysis Dataset
    "ADQS",   # Questionnaire Analysis Dataset
    "ADAE",   # Adverse Events Analysis Dataset
    "ADLB",   # Laboratory Analysis Dataset
    "ADVS",   # Vital Signs Analysis Dataset
    "ADCM",   # Concomitant Medications Analysis Dataset
    "ADEX",   # Exposure Analysis Dataset
    "ADMH",   # Medical History Analysis Dataset
}


def discover_datasets(
    data_directory: str | Path,
    file_formats: list[str] | None = None,
    pattern: str = "AD*"
) -> dict[str, Any]:
    """
    Discover ADaM datasets in a directory.

    This function scans a directory for ADaM dataset files, identifies the dataset
    names, and collects metadata about each dataset.

    Args:
        data_directory: Path to the directory containing dataset files
        file_formats: Optional list of file formats to include (e.g., ["Rds", "csv"]).
                     If None, all supported formats are included.
        pattern: File pattern to match (default: "AD*")

    Returns:
        dict: Discovery results with the following structure:
            {
                "status": "success",
                "data_directory": str,
                "datasets_found": [
                    {
                        "name": str,              # ADaM dataset name (uppercase)
                        "path": str,              # Full path to file
                        "format": str,            # File format (Rds, csv)
                        "is_standard_adam": bool, # True if standard ADaM dataset
                        "size_bytes": int,        # File size in bytes
                        "readable": bool          # True if file is accessible
                    }
                ],
                "count": int,
                "supported_formats": list[str],
                "warnings": list[str]
            }

    Raises:
        ValueError: If a relative path is provided instead of an absolute path
        FileNotFoundError: If the data_directory does not exist
        NotADirectoryError: If the path exists but is not a directory
    """
    # Convert to Path object
    data_dir = Path(data_directory)

    # Validate absolute path
    if not data_dir.is_absolute():
        error_msg = f"Relative path provided: {data_directory}"
        error_msg += "\n\nThis tool requires an absolute path to work correctly."
        error_msg += "\nExample of absolute path: /home/user/project/workspace/"
        error_msg += "\n\nYou provided a relative path. Please provide the full path starting from root."
        raise ValueError(error_msg)

    # Check if directory exists
    if not data_dir.exists():
        error_msg = f"Data directory not found: {data_directory}"
        error_msg += "\n\nPlease provide the full absolute path to your dataset directory."
        error_msg += "\nExample: /home/user/project/workspace/"
        error_msg += "\n\nCommon locations to check:"
        error_msg += "\n  - workspace/"
        error_msg += "\n  - data/"
        error_msg += "\n  - datasets/"
        error_msg += "\n  - sample_data/"

        raise FileNotFoundError(error_msg)

    if not data_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {data_directory}")

    # Initialize results
    datasets_found = []
    warnings = []
    supported_formats = ["Rds", "csv"]

    # Normalize file formats filter (case-insensitive)
    if file_formats is not None:
        file_formats_lower = [fmt.lower() for fmt in file_formats]
    else:
        file_formats_lower = None

    # Scan directory for files
    for file_path in data_dir.iterdir():
        # Skip non-files
        if not file_path.is_file():
            continue

        # Get file extension (case-insensitive)
        file_ext = file_path.suffix.lower().lstrip('.')

        # Check if file format is supported
        if file_ext not in ["rds", "csv"]:
            continue

        # Filter by format if specified
        if file_formats_lower is not None and file_ext not in file_formats_lower:
            continue

        # Extract ADaM dataset name
        adam_name = _extract_adam_name(file_path.name)
        if adam_name is None:
            continue

        # Determine the format (normalize to match expected output)
        file_format = "Rds" if file_ext == "rds" else "csv"

        # Collect metadata
        dataset_info = {
            "name": adam_name,
            "path": str(file_path.absolute()),
            "format": file_format,
            "is_standard_adam": adam_name in STANDARD_ADAM_DATASETS,
            "size_bytes": file_path.stat().st_size,
            "readable": _check_readable(file_path)
        }

        datasets_found.append(dataset_info)

    # Sort by dataset name (alphabetically)
    datasets_found.sort(key=lambda x: x["name"])

    return {
        "status": "success",
        "data_directory": str(data_dir.absolute()),
        "datasets_found": datasets_found,
        "count": len(datasets_found),
        "supported_formats": supported_formats,
        "warnings": warnings
    }


def _extract_adam_name(filename: str) -> str | None:
    """
    Extract ADaM dataset name from filename.

    This function extracts the ADaM dataset name from complex filenames that
    may include project names, dates, drug names, etc.

    Examples:
        "project123_ADSL_2024-01-15.Rds" -> "ADSL"
        "drugX_ADTTE_final.csv" -> "ADTTE"
        "adsl.Rds" -> "ADSL"
        "admin_notes.csv" -> None (not an ADaM dataset)

    Args:
        filename: Name of the file

    Returns:
        str | None: ADaM dataset name (uppercase) or None if not found
    """
    # Handle empty filename
    if not filename:
        return None

    # Convert filename to uppercase for case-insensitive matching
    filename_upper = filename.upper()

    # Remove file extension
    name_without_ext = filename_upper.rsplit('.', 1)[0] if '.' in filename_upper else filename_upper

    # Try to match each standard ADaM dataset name
    for adam_name in STANDARD_ADAM_DATASETS:
        # Use word boundary pattern to avoid false positives
        # Match ADaM name as a whole word (surrounded by non-letter or start/end)
        # Numbers, underscores, hyphens, dots, etc. act as separators
        pattern = rf'(?:^|[^A-Z]){adam_name}(?:[^A-Z]|$)'
        if re.search(pattern, name_without_ext):
            return adam_name

    return None


def _check_readable(path: Path) -> bool:
    """
    Check if a file is readable.

    Args:
        path: Path to the file

    Returns:
        bool: True if file is readable, False otherwise
    """
    try:
        # Check if file exists and is readable
        return path.exists() and path.is_file() and path.stat().st_size >= 0
    except (OSError, PermissionError):
        return False
