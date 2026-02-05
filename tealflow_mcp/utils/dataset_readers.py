"""
Dataset readers for different file formats.

Each reader returns a standardized DatasetInfo structure with columns,
row count, and file metadata.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ColumnInfo:
    """Information about a single column."""

    name: str
    """Column name."""

    type: str
    """Data type (R type like 'character', 'numeric' or Python type like 'object', 'int64')."""

    sample_values: list[str] | None = None
    """Optional sample values (first 5 unique values)."""


@dataclass
class DatasetInfo:
    """Standardized dataset information."""

    columns: list[ColumnInfo]
    """List of column information."""

    row_count: int
    """Number of rows in the dataset."""

    file_size_bytes: int
    """File size in bytes."""


def _read_rds_dataset(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from an RDS file using R.

    Args:
        file_path: Path to the RDS file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with column information

    Raises:
        FileNotFoundError: If Rscript is not found
        ValueError: If the file cannot be read or is not a valid RDS file
    """
    pass


def _read_csv_dataset(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from a CSV file.

    Args:
        file_path: Path to the CSV file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with column information

    Raises:
        ValueError: If the file cannot be read or is not a valid CSV file
    """
    pass


def read_dataset_info(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from a file (dispatches to appropriate reader).

    Args:
        file_path: Path to the dataset file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with standardized structure

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    # Dispatch to appropriate reader based on extension
    ext = file_path.suffix.lower()

    if ext == ".rds":
        return _read_rds_dataset(file_path, include_sample_values)
    elif ext == ".csv":
        return _read_csv_dataset(file_path, include_sample_values)
    else:
        raise ValueError(
            f"Unsupported file format: {ext}. Supported formats: .rds, .csv"
        )
