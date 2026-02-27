"""
Dataset readers for different file formats.

Each reader returns a standardized DatasetInfo structure with columns,
row count, and file metadata.
"""

import datetime
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rdata
from rdata.conversion import DEFAULT_CLASS_MAP, SimpleConverter


def _date_constructor(obj: Any, attrs: Mapping[str, Any]) -> Any:
    """
    Custom constructor for R Date class.

    R Date stores dates as days since 1970-01-01.
    Converts to pandas datetime64[ns] with date precision.
    Handles NaN values without triggering RuntimeWarning.
    Stores original R class in Series.attrs for accurate type inference.
    """
    obj_array = np.asarray(obj, dtype=float)
    mask = ~np.isnan(obj_array)

    # Create result series with NaT for all positions
    result = pd.Series(pd.NaT, index=range(len(obj_array)), dtype="datetime64[ns]")

    # Convert only non-NaN values
    if mask.any():
        origin = pd.Timestamp("1970-01-01")
        result[mask] = pd.to_datetime(obj_array[mask], unit="D", origin=origin, errors="coerce")

    # Store original R class in attrs for accurate type inference
    # This prevents misclassification of POSIXct columns that happen to have all midnight values
    result.attrs["r_class"] = "Date"

    return result


def _posixct_constructor(obj: Any, attrs: Mapping[str, Any]) -> Any:
    """
    Custom constructor for R POSIXct class.

    R POSIXct stores datetimes as seconds since 1970-01-01 UTC.
    Converts to pandas datetime64[ns].
    Handles NaN values without triggering RuntimeWarning.
    Stores original R class in Series.attrs for accurate type inference.
    """
    obj_array = np.asarray(obj, dtype=float)
    mask = ~np.isnan(obj_array)

    # Create result series with NaT for all positions
    result = pd.Series(pd.NaT, index=range(len(obj_array)), dtype="datetime64[ns]")

    # Convert only non-NaN values
    if mask.any():
        result[mask] = pd.to_datetime(obj_array[mask], unit="s", errors="coerce")

    # Store original R class in attrs for accurate type inference
    # This prevents misclassification of POSIXct columns that happen to have all midnight values
    result.attrs["r_class"] = "POSIXct"

    return result


# Custom class map with Date and POSIXct support
_RDATA_CLASS_MAP = DEFAULT_CLASS_MAP.copy()
_RDATA_CLASS_MAP["Date"] = _date_constructor
_RDATA_CLASS_MAP["POSIXct"] = _posixct_constructor
_RDATA_CLASS_MAP["POSIXt"] = _posixct_constructor  # POSIXt is parent class


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

    R data readers may convert numeric columns with NA values to object dtype.
    This function checks if non-null values can be converted to numeric or are date objects.

    Args:
        col_data: pandas Series with object dtype

    Returns:
        "integer", "numeric", "date", or "character"
    """
    # Get non-null values
    non_null = col_data.dropna()

    # If all values are null, default to character
    if len(non_null) == 0:
        return "character"

    # Check if values are date/datetime objects
    # Sample first few values to determine if this is a date column
    sample = non_null.head(min(10, len(non_null)))
    if all(isinstance(val, (datetime.date, datetime.datetime)) for val in sample):
        # Check if all are date objects (not datetime with time component)
        if all(
            isinstance(val, datetime.date) and not isinstance(val, datetime.datetime)
            for val in sample
        ):
            return "date"
        else:
            # Has datetime objects, should have been caught earlier as POSIXct
            return "POSIXct"

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


def _infer_datetime_type(col_data: pd.Series) -> str:
    """
    Infer whether a datetime column is R Date or POSIXct.

    First checks Series.attrs for the original R class stored during rdata conversion.
    This prevents misclassification of POSIXct columns that legitimately have all
    midnight timestamps.

    Falls back to heuristic (time component check) for datetime data from other sources
    (e.g., CSV files, manual series creation).

    Args:
        col_data: pandas Series with datetime dtype

    Returns:
        "date" or "POSIXct"
    """
    # Check if original R class is stored in attrs (from rdata conversion)
    if hasattr(col_data, "attrs") and "r_class" in col_data.attrs:
        r_class = col_data.attrs["r_class"]
        if r_class == "Date":
            return "date"
        elif r_class == "POSIXct":
            return "POSIXct"

    # Fallback: use heuristic for data from other sources (e.g., CSV, manual creation)
    # Get non-null values
    non_null = col_data.dropna()

    if len(non_null) == 0:
        # Default to POSIXct for empty columns
        return "POSIXct"

    # Sample values to check for time component
    sample = non_null.head(min(100, len(non_null)))

    # Check if all times are exactly midnight (00:00:00)
    # This heuristic suggests it's likely a Date (date-only) rather than POSIXct
    # Note: This can misclassify POSIXct with all midnight values, but that's
    # acceptable for non-R data sources where we don't have the original class info
    try:
        # For datetime64, check if time components are all zero
        times = pd.to_datetime(sample)
        all_midnight = (
            (times.dt.hour == 0).all()
            and (times.dt.minute == 0).all()
            and (times.dt.second == 0).all()
            and (times.dt.microsecond == 0).all()
            and (times.dt.nanosecond == 0).all()
        )
        return "date" if all_midnight else "POSIXct"
    except Exception:
        return "POSIXct"


def _read_rds_dataset(file_path: Path, include_sample_values: bool = False) -> DatasetInfo:
    """
    Read dataset information from an RDS file using rdata.

    Args:
        file_path: Path to the RDS file
        include_sample_values: Whether to include sample values for each column

    Returns:
        DatasetInfo object with column information

    Raises:
        ValueError: If the file cannot be read or is not a valid RDS file
    """
    try:
        # Read RDS file using rdata with custom converters for Date/POSIXct
        # Parse the file first, then convert with our custom class map
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            parsed = rdata.parser.parse_file(file_path)
            converter = SimpleConverter(constructor_dict=_RDATA_CLASS_MAP)
            df = converter.convert(parsed)

        # Verify we got a DataFrame
        if df is None:
            raise ValueError("RDS file contains no data")

        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"RDS file does not contain a DataFrame, got {type(df).__name__}")

        # Extract column information
        columns = []
        for col_name in df.columns:
            col_data = df[col_name]

            # Get pandas dtype and convert to R-like type name
            dtype = str(col_data.dtype).lower()

            # Map pandas dtypes to R-like types
            # Note: rdata uses nullable integer types (Int32, Int64) which become lowercase here
            if dtype.startswith("int"):
                r_type = "integer"
            elif dtype.startswith("float"):
                r_type = "numeric"
            elif dtype == "object":
                # For object dtype, try to infer if it's actually numeric
                # R data readers may convert numeric columns with NAs to object dtype
                r_type = _infer_object_type(col_data)
            elif dtype in ("bool", "boolean"):
                r_type = "logical"
            elif dtype.startswith("datetime"):
                # Distinguish between Date (date-only) and POSIXct (datetime)
                # Date columns have no time component (all times are midnight)
                r_type = _infer_datetime_type(col_data)
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
