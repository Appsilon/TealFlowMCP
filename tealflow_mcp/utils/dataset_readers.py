"""
Dataset readers for different file formats.

Each reader returns a standardized DatasetInfo structure with columns,
row count, and file metadata.
"""

import warnings
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyreadr


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


def _infer_object_type(col_data: pd.Series) -> str:
    """
    Infer the R type for an object dtype column.

    pyreadr converts numeric columns with NA values to object dtype.
    This function checks if non-null values can be converted to numeric.

    Args:
        col_data: pandas Series with object dtype

    Returns:
        "integer", "numeric", or "character"
    """
    # Get non-null values
    non_null = col_data.dropna()

    # If all values are null, default to character
    if len(non_null) == 0:
        return "character"

    # Try to convert to numeric
    try:
        numeric_values = pd.to_numeric(non_null, errors="raise")

        # Check if all numeric values are integers
        if (numeric_values == numeric_values.astype(int)).all():
            return "integer"
        else:
            return "numeric"
    except (ValueError, TypeError):
        # Not numeric, it's character
        return "character"


def _read_rds_dataset(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from an RDS file using pyreadr.

    Args:
        file_path: Path to the RDS file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with column information

    Raises:
        ValueError: If the file cannot be read or is not a valid RDS file
    """
    try:
        # Read RDS file using pyreadr
        # Suppress RuntimeWarning from pyreadr's datetime conversion with NaT values
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="invalid value encountered in cast")
            result = pyreadr.read_r(str(file_path))

        # pyreadr returns a dict, get the first (and usually only) dataframe
        if not result:
            raise ValueError("RDS file contains no data")

        # Get the first dataframe
        df = next(iter(result.values()))

        # Extract column information
        columns = []
        for col_name in df.columns:
            col_data = df[col_name]

            # Get pandas dtype and convert to R-like type name
            dtype = str(col_data.dtype)

            # Map pandas dtypes to R-like types
            if dtype.startswith("int"):
                r_type = "integer"
            elif dtype.startswith("float"):
                r_type = "numeric"
            elif dtype == "object":
                # For object dtype, try to infer if it's actually numeric
                # pyreadr converts numeric columns with NAs to object dtype
                r_type = _infer_object_type(col_data)
            elif dtype == "bool":
                r_type = "logical"
            elif dtype.startswith("datetime"):
                r_type = "POSIXct"
            else:
                r_type = dtype

            # Get sample values if requested
            sample_values = None
            if include_sample_values:
                # Get unique non-null values, limit to 5
                unique_vals = col_data.dropna().unique()[:5]
                sample_values = [str(val) for val in unique_vals]

            columns.append(
                ColumnInfo(
                    name=col_name,
                    type=r_type,
                    sample_values=sample_values,
                )
            )

        # Get file size
        file_size = file_path.stat().st_size

        return DatasetInfo(
            columns=columns,
            row_count=len(df),
            file_size_bytes=file_size,
        )

    except Exception as e:
        raise ValueError(f"Failed to read RDS file: {e}") from e


def _read_csv_dataset(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from a CSV file using pandas.

    Args:
        file_path: Path to the CSV file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with column information

    Raises:
        ValueError: If the file cannot be read or is not a valid CSV file
    """
    try:
        # Read CSV file using pandas
        df = pd.read_csv(file_path)

        # Check if dataframe is empty
        if df.empty:
            raise ValueError("CSV file is empty or contains no data")

        # Extract column information
        columns = []
        for col_name in df.columns:
            col_data = df[col_name]

            # Get pandas dtype
            dtype = str(col_data.dtype)

            # Map pandas dtypes to simpler type names
            if dtype.startswith("int"):
                type_name = "integer"
            elif dtype.startswith("float"):
                type_name = "numeric"
            elif dtype == "object":
                # For object dtype, try to infer if it's actually numeric
                # Some CSV files may have numeric data stored as strings
                type_name = _infer_object_type(col_data)
            elif dtype in ["str", "string"]:
                # Pandas 2.x string dtype
                type_name = "character"
            elif dtype == "bool":
                type_name = "logical"
            elif dtype.startswith("datetime"):
                type_name = "datetime"
            else:
                type_name = dtype

            # Get sample values if requested
            sample_values = None
            if include_sample_values:
                # Get unique non-null values, limit to 5
                unique_vals = col_data.dropna().unique()[:5]
                sample_values = [str(val) for val in unique_vals]

            columns.append(
                ColumnInfo(
                    name=col_name,
                    type=type_name,
                    sample_values=sample_values,
                )
            )

        # Get file size
        file_size = file_path.stat().st_size

        return DatasetInfo(
            columns=columns,
            row_count=len(df),
            file_size_bytes=file_size,
        )

    except pd.errors.EmptyDataError as e:
        raise ValueError("CSV file is empty") from e
    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is for proper error handling
        raise
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}") from e


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
        raise ValueError(f"Unsupported file format: {ext}. Supported formats: .rds, .csv")
