"""
Unit tests for dataset readers.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from tealflow_mcp.utils import ColumnInfo, DatasetInfo, read_dataset_info
from tealflow_mcp.utils.dataset_readers import _read_csv_dataset, _read_rds_dataset

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
