"""
Unit tests for dataset readers.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from tealflow_mcp.utils import ColumnInfo, DatasetInfo, read_dataset_info
from tealflow_mcp.utils.dataset_readers import (
    _infer_object_type,
    _read_csv_dataset,
    _read_rds_dataset,
)

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestDatasetInfo:
    """Test DatasetInfo and ColumnInfo dataclasses."""

    def test_column_info_creation(self):
        """Test creating a ColumnInfo object."""
        col = ColumnInfo(name="USUBJID", type="character")
        assert col.name == "USUBJID"
        assert col.type == "character"
        assert col.sample_values is None

    def test_column_info_with_samples(self):
        """Test creating a ColumnInfo object with sample values."""
        col = ColumnInfo(name="AGE", type="numeric", sample_values=["25", "30", "45", "50", "60"])
        assert col.name == "AGE"
        assert col.type == "numeric"
        assert len(col.sample_values) == 5

    def test_dataset_info_creation(self):
        """Test creating a DatasetInfo object."""
        columns = [
            ColumnInfo(name="USUBJID", type="character"),
            ColumnInfo(name="AGE", type="numeric"),
        ]
        info = DatasetInfo(columns=columns, row_count=100, file_size_bytes=1024)
        assert len(info.columns) == 2
        assert info.row_count == 100
        assert info.file_size_bytes == 1024


class TestReadDatasetInfoDispatcher:
    """Test the read_dataset_info dispatcher function."""

    def test_file_not_found(self):
        """Test error when file does not exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            read_dataset_info(Path("/nonexistent/file.rds"))
        assert "Dataset file not found" in str(exc_info.value)

    def test_unsupported_format(self):
        """Test error for unsupported file formats."""
        with TemporaryDirectory() as tmpdir:
            # Create a file with unsupported extension
            unsupported_file = Path(tmpdir) / "data.xlsx"
            unsupported_file.touch()

            with pytest.raises(ValueError) as exc_info:
                read_dataset_info(unsupported_file)
            assert "Unsupported file format: .xlsx" in str(exc_info.value)
            assert "Supported formats: .rds, .csv" in str(exc_info.value)

    def test_dispatches_to_rds_reader(self):
        """Test that .rds files are dispatched to RDS reader."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"

        # Should successfully dispatch to RDS reader
        result = read_dataset_info(adsl_file)

        assert isinstance(result, DatasetInfo)
        assert len(result.columns) > 0
        assert result.row_count > 0

    def test_dispatches_to_csv_reader(self):
        """Test that .csv files are dispatched to CSV reader."""
        csv_file = FIXTURES_DIR / "test_basic.csv"

        # Should successfully dispatch to CSV reader
        result = read_dataset_info(csv_file)

        assert isinstance(result, DatasetInfo)
        assert len(result.columns) == 3
        assert result.row_count > 0

    def test_case_insensitive_extension(self):
        """Test that file extensions are case-insensitive."""
        # Test with uppercase extensions using existing fixtures
        # Create temporary copies with uppercase extensions
        with TemporaryDirectory() as tmpdir:
            # Copy ADSL.Rds to data.RDS
            import shutil

            rds_source = FIXTURES_DIR / "ADSL.Rds"
            rds_file = Path(tmpdir) / "data.RDS"
            shutil.copy(rds_source, rds_file)

            result = read_dataset_info(rds_file)
            assert isinstance(result, DatasetInfo)

            # Copy test_basic.csv to data.CSV
            csv_source = FIXTURES_DIR / "test_basic.csv"
            csv_file = Path(tmpdir) / "data.CSV"
            shutil.copy(csv_source, csv_file)

            result = read_dataset_info(csv_file)
            assert isinstance(result, DatasetInfo)


class TestReadRdsDataset:
    """Test _read_rds_dataset function."""

    def test_basic_rds_file(self):
        """Test reading a basic RDS file."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = _read_rds_dataset(adsl_file, include_sample_values=False)

        # Should return DatasetInfo
        assert isinstance(result, DatasetInfo)

        # Should have columns
        assert len(result.columns) > 0

        # All columns should have names and types
        for col in result.columns:
            assert col.name
            assert col.type
            assert col.sample_values is None  # Not requested

        # Should have positive row count
        assert result.row_count > 0

        # Should have file size
        assert result.file_size_bytes > 0

    def test_rds_with_sample_values(self):
        """Test reading RDS file with sample values."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = _read_rds_dataset(adsl_file, include_sample_values=True)

        # Should have sample values for each column
        for col in result.columns:
            assert col.sample_values is not None
            assert isinstance(col.sample_values, list)
            assert len(col.sample_values) <= 5  # Max 5 samples

    def test_rds_file_not_found(self):
        """Test error when RDS file doesn't exist."""
        with pytest.raises((FileNotFoundError, ValueError)):
            _read_rds_dataset(Path("/nonexistent/file.rds"))

    def test_invalid_rds_file(self):
        """Test error with invalid RDS file."""
        invalid_rds = FIXTURES_DIR / "invalid.rds"
        with pytest.raises(ValueError):
            _read_rds_dataset(invalid_rds)


class TestReadCsvDataset:
    """Test _read_csv_dataset function."""

    def test_basic_csv_file(self):
        """Test reading a basic CSV file."""
        csv_file = FIXTURES_DIR / "test_basic.csv"
        result = _read_csv_dataset(csv_file, include_sample_values=False)

        # Should return DatasetInfo
        assert isinstance(result, DatasetInfo)

        # Should have 3 columns
        assert len(result.columns) == 3

        # Check column names
        col_names = [col.name for col in result.columns]
        assert "USUBJID" in col_names
        assert "AGE" in col_names
        assert "SEX" in col_names

        # All columns should have types
        for col in result.columns:
            assert col.type
            assert col.sample_values is None  # Not requested

        # Should have 3 rows
        assert result.row_count == 3

        # Should have file size
        assert result.file_size_bytes > 0

    def test_csv_with_sample_values(self):
        """Test reading CSV file with sample values."""
        csv_file = FIXTURES_DIR / "test_with_samples.csv"
        result = _read_csv_dataset(csv_file, include_sample_values=True)

        # Should have sample values
        for col in result.columns:
            assert col.sample_values is not None
            assert isinstance(col.sample_values, list)
            assert len(col.sample_values) <= 5

    def test_csv_file_not_found(self):
        """Test error when CSV file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            _read_csv_dataset(Path("/nonexistent/file.csv"))

    def test_invalid_csv_file(self):
        """Test with malformed CSV (different column counts)."""
        with TemporaryDirectory() as tmpdir:
            # Create a file with invalid CSV content
            invalid_csv = Path(tmpdir) / "invalid.csv"
            invalid_csv.write_text("not,valid\ncsv,content,with,wrong,columns\n")

            # Should still work but might have unexpected structure
            result = _read_csv_dataset(invalid_csv)
            assert isinstance(result, DatasetInfo)

    def test_empty_csv_file(self):
        """Test handling of empty CSV file."""
        empty_csv = FIXTURES_DIR / "empty.csv"
        # Should raise an error (exact type depends on implementation)
        with pytest.raises((ValueError, FileNotFoundError)):
            _read_csv_dataset(empty_csv)

    def test_csv_with_missing_values(self):
        """Test CSV file with missing values."""
        csv_file = FIXTURES_DIR / "test_missing.csv"
        result = _read_csv_dataset(csv_file, include_sample_values=True)

        # Should handle missing values gracefully
        assert isinstance(result, DatasetInfo)
        assert len(result.columns) == 3


class TestIntegrationWithRealFiles:
    """Integration tests with real dataset files."""

    def test_reads_sample_adsl_rds(self):
        """Test reading the ADSL.Rds file."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = read_dataset_info(adsl_file, include_sample_values=False)

        assert isinstance(result, DatasetInfo)
        assert len(result.columns) > 0
        assert result.row_count > 0

        # ADSL should have standard columns
        col_names = [col.name for col in result.columns]
        assert "USUBJID" in col_names

    def test_reads_sample_adtte_rds(self):
        """Test reading the ADTTE.Rds file."""
        adtte_file = FIXTURES_DIR / "ADTTE.Rds"
        result = read_dataset_info(adtte_file, include_sample_values=True)

        assert isinstance(result, DatasetInfo)
        assert len(result.columns) > 0

        # Should have sample values
        for col in result.columns:
            assert col.sample_values is not None


class TestInferObjectType:
    """Test the _infer_object_type function for type inference."""

    def test_infer_integer_type(self):
        """Test inferring integer type from object dtype column."""
        # Create a Series with integer values as strings (like pyreadr does with NAs)
        series = pd.Series(["1", "2", "3", None, "4", None], dtype=object)
        result = _infer_object_type(series)
        assert result == "integer"

    def test_infer_numeric_type(self):
        """Test inferring numeric type from object dtype column."""
        # Create a Series with float values as strings
        series = pd.Series(["1.5", "2.7", None, "3.14", "4.2"], dtype=object)
        result = _infer_object_type(series)
        assert result == "numeric"

    def test_infer_character_type(self):
        """Test inferring character type from object dtype column."""
        # Create a Series with actual character data
        series = pd.Series(["abc", "def", None, "ghi"], dtype=object)
        result = _infer_object_type(series)
        assert result == "character"

    def test_infer_with_all_nulls(self):
        """Test that all-null columns default to character."""
        series = pd.Series([None, None, None], dtype=object)
        result = _infer_object_type(series)
        assert result == "character"

    def test_infer_mixed_numeric_strings(self):
        """Test with mixed integer and float values."""
        series = pd.Series(["1", "2.5", None, "3"], dtype=object)
        result = _infer_object_type(series)
        # Should be numeric since not all values are integers
        assert result == "numeric"

    def test_infer_large_integers(self):
        """Test with large integer values."""
        series = pd.Series(["1096", "1083", None, "1078"], dtype=object)
        result = _infer_object_type(series)
        assert result == "integer"

    def test_infer_negative_integers(self):
        """Test with negative integer values."""
        series = pd.Series(["-1", "-2", None, "-3"], dtype=object)
        result = _infer_object_type(series)
        assert result == "integer"

    def test_infer_negative_floats(self):
        """Test with negative float values."""
        series = pd.Series(["-1.5", "-2.7", None, "-3.14"], dtype=object)
        result = _infer_object_type(series)
        assert result == "numeric"

    def test_infer_scientific_notation(self):
        """Test with scientific notation."""
        series = pd.Series(["1e5", "2.5e-3", None], dtype=object)
        result = _infer_object_type(series)
        assert result == "numeric"

    def test_infer_with_whitespace(self):
        """Test that numeric strings with whitespace are handled."""
        series = pd.Series([" 1 ", " 2.5 ", None], dtype=object)
        result = _infer_object_type(series)
        # pd.to_numeric should handle whitespace
        assert result == "numeric"

    def test_infer_mixed_numeric_and_text(self):
        """Test with truly mixed content (some numeric, some text)."""
        series = pd.Series(["1", "abc", None, "3"], dtype=object)
        result = _infer_object_type(series)
        # Should fail numeric conversion and return character
        assert result == "character"

    def test_infer_zero_values(self):
        """Test with zero values."""
        series = pd.Series(["0", "0.0", None], dtype=object)
        result = _infer_object_type(series)
        # Both "0" and "0.0" convert to 0.0, which equals int(0.0), so classified as integer
        assert result == "integer"

    def test_infer_single_value(self):
        """Test with single non-null value."""
        series = pd.Series([None, None, "42", None], dtype=object)
        result = _infer_object_type(series)
        assert result == "integer"

    def test_infer_bool_like_numbers(self):
        """Test with 0/1 values (common for boolean encoding)."""
        series = pd.Series(["0", "1", None, "1", "0"], dtype=object)
        result = _infer_object_type(series)
        assert result == "integer"


class TestTypeInferenceInRdsFiles:
    """Test that type inference works correctly with real RDS files."""

    def test_numeric_columns_with_nas_in_adsl(self):
        """Test that numeric columns with NAs are correctly typed in ADSL.Rds."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = _read_rds_dataset(adsl_file, include_sample_values=False)

        # Find numeric columns that pyreadr would have converted to object
        # These are known columns from ADSL that have NAs
        col_types = {col.name: col.type for col in result.columns}

        # EOSDY, LDDTHELD, DTHADY should be integer, not character
        if "EOSDY" in col_types:
            assert col_types["EOSDY"] == "integer", "EOSDY should be integer type"

        if "LDDTHELD" in col_types:
            assert col_types["LDDTHELD"] == "integer", "LDDTHELD should be integer type"

        if "DTHADY" in col_types:
            assert col_types["DTHADY"] == "integer", "DTHADY should be integer type"

    def test_character_columns_remain_character(self):
        """Test that actual character columns are not misidentified as numeric."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = _read_rds_dataset(adsl_file, include_sample_values=False)

        # Find actual character columns
        col_types = {col.name: col.type for col in result.columns}

        # USUBJID should remain character (contains IDs like 'AB12345-CHN-2-id-22')
        if "USUBJID" in col_types:
            assert col_types["USUBJID"] in ["character", "category"], (
                "USUBJID should be character or category, not numeric"
            )

    def test_no_false_numeric_inference(self):
        """Test that we don't have any false positives (character typed as numeric)."""
        adsl_file = FIXTURES_DIR / "ADSL.Rds"
        result = _read_rds_dataset(adsl_file, include_sample_values=True)

        # Check that columns with text samples aren't typed as numeric/integer
        for col in result.columns:
            if col.type in ["integer", "numeric"] and col.sample_values:
                # If it's typed as numeric, sample values should be numeric
                for sample in col.sample_values:
                    # Should be able to convert to float
                    try:
                        float(sample)
                    except ValueError:
                        pytest.fail(
                            f"Column {col.name} is typed as {col.type} "
                            f"but has non-numeric sample: {sample}"
                        )


class TestCsvTypeInference:
    """Test that type inference works correctly with CSV files."""

    def test_csv_numeric_columns_with_nas(self):
        """Test that CSV numeric columns with NAs are correctly typed."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_numeric_na.csv"

            # Create CSV with numeric columns containing NAs
            df = pd.DataFrame(
                {
                    "ID": [1, 2, 3, 4, 5],
                    "AGE": [25, 30, None, 35, 40],
                    "WEIGHT": [70.5, None, 80.2, 75.0, None],
                    "COUNT": [10, 20, None, 40, 50],
                }
            )
            df.to_csv(csv_path, index=False)

            # Read with our reader
            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # All numeric columns should be typed as numeric (pandas converts int+NA to float64)
            assert col_types["ID"] == "integer"
            assert col_types["AGE"] == "numeric"  # int + NA = float64
            assert col_types["WEIGHT"] == "numeric"
            assert col_types["COUNT"] == "numeric"  # int + NA = float64

    def test_csv_quoted_numeric_strings(self):
        """Test CSV with quoted numeric strings."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_quoted.csv"

            # Create CSV with quoted numeric values
            csv_content = """ID,VALUE1,VALUE2,TEXT
1,"123","45.6","abc"
2,"234","56.7","def"
3,"345","67.8","ghi"
"""
            csv_path.write_text(csv_content)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # Pandas should automatically infer these as numeric
            assert col_types["ID"] == "integer"
            assert col_types["VALUE1"] == "integer"
            assert col_types["VALUE2"] == "numeric"
            assert col_types["TEXT"] == "character"

    def test_csv_mixed_numeric_and_text(self):
        """Test CSV with truly mixed numeric and text values."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_mixed.csv"

            csv_content = """ID,MIXED_COL
1,text
2,123
3,another
4,456
"""
            csv_path.write_text(csv_content)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # MIXED_COL should be character (object dtype with mixed content)
            assert col_types["MIXED_COL"] == "character"

    def test_csv_whitespace_numeric(self):
        """Test CSV with numeric values that have whitespace."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_whitespace.csv"

            csv_content = """ID,SPACES
1," 123 "
2," 234 "
3," 345 "
"""
            csv_path.write_text(csv_content)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # SPACES column will be object dtype, but _infer_object_type should detect numeric
            # Note: pandas may trim whitespace automatically, making it numeric
            assert col_types["SPACES"] in ["integer", "character"]

    def test_csv_empty_strings_as_na(self):
        """Test CSV with empty strings treated as NA."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_empty.csv"

            csv_content = """ID,VALUE
1,123
2,
3,234
4,
5,345
"""
            csv_path.write_text(csv_content)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # VALUE column should be numeric (pandas treats empty as NaN)
            assert col_types["VALUE"] == "numeric"

    def test_csv_boolean_as_numeric(self):
        """Test CSV with 0/1 values (common boolean encoding)."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_bool.csv"

            df = pd.DataFrame({"ID": [1, 2, 3, 4], "FLAG": [0, 1, 1, 0]})
            df.to_csv(csv_path, index=False)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # FLAG should be integer (0/1 are integers)
            assert col_types["FLAG"] == "integer"

    def test_csv_scientific_notation(self):
        """Test CSV with scientific notation."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_scientific.csv"

            df = pd.DataFrame({"ID": [1, 2, 3], "VALUE": [1e5, 2.5e-3, 3.14e2]})
            df.to_csv(csv_path, index=False)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # Scientific notation should be numeric
            assert col_types["VALUE"] == "numeric"

    def test_csv_large_integers(self):
        """Test CSV with large integer values."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_large_int.csv"

            df = pd.DataFrame({"ID": [1, 2, 3], "LARGE": [1234567890, 9876543210, 1111111111]})
            df.to_csv(csv_path, index=False)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # Large integers should be integer
            assert col_types["LARGE"] == "integer"

    def test_csv_negative_values(self):
        """Test CSV with negative values."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_negative.csv"

            df = pd.DataFrame(
                {
                    "ID": [1, 2, 3],
                    "INT_NEG": [-10, -20, -30],
                    "FLOAT_NEG": [-1.5, -2.7, -3.14],
                }
            )
            df.to_csv(csv_path, index=False)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # Negative values should maintain their type
            assert col_types["INT_NEG"] == "integer"
            assert col_types["FLOAT_NEG"] == "numeric"

    def test_csv_all_na_column(self):
        """Test CSV with a column that's all NA."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test_all_na.csv"

            df = pd.DataFrame({"ID": [1, 2, 3], "ALL_NA": [None, None, None]})
            df.to_csv(csv_path, index=False)

            result = _read_csv_dataset(csv_path, include_sample_values=False)
            col_types = {col.name: col.type for col in result.columns}

            # All-NA column defaults to character
            assert col_types["ALL_NA"] in ["character", "numeric"]  # pandas may use float


class TestDatasetInfoStructure:
    """Test the structure and consistency of DatasetInfo output."""

    def test_all_columns_have_names(self):
        """Test that all columns have non-empty names."""
        csv_file = FIXTURES_DIR / "test_basic.csv"
        result = _read_csv_dataset(csv_file)

        for col in result.columns:
            assert col.name
            assert len(col.name) > 0

    def test_all_columns_have_types(self):
        """Test that all columns have non-empty types."""
        csv_file = FIXTURES_DIR / "test_basic.csv"
        result = _read_csv_dataset(csv_file)

        for col in result.columns:
            assert col.type
            assert len(col.type) > 0

    def test_row_count_is_positive(self):
        """Test that row count is a positive integer."""
        csv_file = FIXTURES_DIR / "test_basic.csv"
        result = _read_csv_dataset(csv_file)

        assert isinstance(result.row_count, int)
        assert result.row_count > 0
        assert result.row_count == 3

    def test_file_size_is_positive(self):
        """Test that file size is a positive integer."""
        csv_file = FIXTURES_DIR / "test_basic.csv"
        result = _read_csv_dataset(csv_file)

        assert isinstance(result.file_size_bytes, int)
        assert result.file_size_bytes > 0

    def test_sample_values_are_strings(self):
        """Test that sample values are always strings."""
        csv_file = FIXTURES_DIR / "test_types.csv"
        result = _read_csv_dataset(csv_file, include_sample_values=True)

        for col in result.columns:
            if col.sample_values:
                for val in col.sample_values:
                    assert isinstance(val, str)

    def test_sample_values_limited_to_five(self):
        """Test that sample values are limited to 5 items."""
        csv_file = FIXTURES_DIR / "test_many_rows.csv"
        result = _read_csv_dataset(csv_file, include_sample_values=True)

        for col in result.columns:
            if col.sample_values:
                assert len(col.sample_values) <= 5
