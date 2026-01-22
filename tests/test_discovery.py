"""
Unit tests for dataset discovery functionality.

Tests the core discovery logic for finding ADaM datasets in a directory.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestDatasetDiscovery:
    """Test dataset discovery functionality."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_discover_rds_files(self, temp_data_dir):
        """Test discovering RDS files in a directory."""
        # Create test RDS files
        (temp_data_dir / "ADSL.Rds").touch()
        (temp_data_dir / "ADTTE.Rds").touch()

        # Import here to avoid import errors before implementation
        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["datasets_found"]) == 2

        # Check dataset names
        names = [ds["name"] for ds in result["datasets_found"]]
        assert "ADSL" in names
        assert "ADTTE" in names

        # Check formats
        for ds in result["datasets_found"]:
            assert ds["format"] == "Rds"

    def test_discover_csv_files(self, temp_data_dir):
        """Test discovering CSV files in a directory."""
        # Create test CSV files
        (temp_data_dir / "ADSL.csv").touch()
        (temp_data_dir / "ADAE.csv").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 2

        # Check formats
        for ds in result["datasets_found"]:
            assert ds["format"] == "csv"

    def test_discover_mixed_formats(self, temp_data_dir):
        """Test discovering mixed RDS and CSV files."""
        # Create mixed format files
        (temp_data_dir / "ADSL.Rds").touch()
        (temp_data_dir / "ADTTE.csv").touch()
        (temp_data_dir / "ADAE.Rds").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 3

        # Check we have both formats
        formats = [ds["format"] for ds in result["datasets_found"]]
        assert "Rds" in formats
        assert "csv" in formats

    def test_discover_ignores_non_adam_files(self, temp_data_dir):
        """Test that non-ADaM files are ignored."""
        # Create ADaM files
        (temp_data_dir / "ADSL.Rds").touch()
        # Create non-ADaM files
        (temp_data_dir / "README.md").touch()
        (temp_data_dir / "data.txt").touch()
        (temp_data_dir / "config.json").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["datasets_found"][0]["name"] == "ADSL"

    def test_discover_identifies_standard_adam(self, temp_data_dir):
        """Test that standard ADaM datasets are identified."""
        # Create standard ADaM files
        (temp_data_dir / "ADSL.Rds").touch()
        (temp_data_dir / "ADTTE.Rds").touch()
        # Create non-standard ADaM file
        (temp_data_dir / "ADCUSTOM.Rds").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 3

        # Check standard vs non-standard
        for ds in result["datasets_found"]:
            if ds["name"] in ["ADSL", "ADTTE"]:
                assert ds["is_standard_adam"] is True
            elif ds["name"] == "ADCUSTOM":
                assert ds["is_standard_adam"] is False

    def test_discover_empty_directory(self, temp_data_dir):
        """Test discovering in an empty directory."""
        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 0
        assert result["datasets_found"] == []

    def test_discover_missing_directory(self):
        """Test error handling for non-existent directory."""
        from tealflow_mcp.tools.discovery import discover_datasets

        with pytest.raises(FileNotFoundError):
            discover_datasets("/path/that/does/not/exist")

    def test_discover_returns_metadata(self, temp_data_dir):
        """Test that discovery returns proper metadata for each dataset."""
        # Create test file
        test_file = temp_data_dir / "ADSL.Rds"
        test_file.write_text("test data")

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["count"] == 1
        dataset = result["datasets_found"][0]

        # Check required metadata fields
        assert "name" in dataset
        assert "path" in dataset
        assert "format" in dataset
        assert "is_standard_adam" in dataset
        assert "size_bytes" in dataset
        assert "readable" in dataset

        # Check metadata values
        assert dataset["name"] == "ADSL"
        assert dataset["format"] == "Rds"
        assert dataset["size_bytes"] > 0
        assert dataset["readable"] is True

    def test_discover_with_format_filter(self, temp_data_dir):
        """Test filtering by file format."""
        # Create mixed formats
        (temp_data_dir / "ADSL.Rds").touch()
        (temp_data_dir / "ADTTE.csv").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        # Filter for RDS only
        result = discover_datasets(temp_data_dir, file_formats=["Rds"])

        assert result["count"] == 1
        assert result["datasets_found"][0]["format"] == "Rds"

    def test_discover_sorts_by_name(self, temp_data_dir):
        """Test that results are sorted by dataset name."""
        # Create files in non-alphabetical order
        (temp_data_dir / "ADTTE.Rds").touch()
        (temp_data_dir / "ADAE.Rds").touch()
        (temp_data_dir / "ADSL.Rds").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        names = [ds["name"] for ds in result["datasets_found"]]
        assert names == sorted(names)

    def test_discover_complex_filenames(self, temp_data_dir):
        """Test that ADaM names are extracted from complex filenames."""
        # Create files with project names, dates, drug names, etc.
        (temp_data_dir / "project123_ADSL_2024-01-15.Rds").touch()
        (temp_data_dir / "drugX_ADTTE_final.csv").touch()
        (temp_data_dir / "ADAE_v2_locked.Rds").touch()
        (temp_data_dir / "study_abc_ADRS.csv").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 4

        # Check that ADaM names were correctly extracted
        names = {ds["name"] for ds in result["datasets_found"]}
        assert names == {"ADSL", "ADTTE", "ADAE", "ADRS"}

    def test_discover_case_insensitive(self, temp_data_dir):
        """Test that discovery is case-insensitive for ADaM dataset names."""
        # Create files with various case variations
        (temp_data_dir / "adsl.Rds").touch()
        (temp_data_dir / "AdTtE.csv").touch()
        (temp_data_dir / "ADAE.Rds").touch()
        (temp_data_dir / "project_adrs_final.csv").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 4

        # Check that names are normalized (should be uppercase)
        names = {ds["name"] for ds in result["datasets_found"]}
        assert names == {"ADSL", "ADTTE", "ADAE", "ADRS"}

    def test_discover_complex_and_simple_mixed(self, temp_data_dir):
        """Test that both simple and complex filenames are handled."""
        # Mix of simple and complex naming
        (temp_data_dir / "ADSL.Rds").touch()
        (temp_data_dir / "study123_ADTTE_locked.csv").touch()
        (temp_data_dir / "ADAE.Rds").touch()
        (temp_data_dir / "final_ADRS_v3.csv").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 4

        names = {ds["name"] for ds in result["datasets_found"]}
        assert names == {"ADSL", "ADTTE", "ADAE", "ADRS"}

    def test_discover_avoids_false_positives(self, temp_data_dir):
        """Test that files with 'AD' but not ADaM datasets are ignored."""
        # These should NOT be detected as ADaM datasets
        (temp_data_dir / "README.txt").touch()
        (temp_data_dir / "admin_notes.csv").touch()
        (temp_data_dir / "data_loading.R").touch()
        (temp_data_dir / "advanced_analysis.Rds").touch()

        # This SHOULD be detected
        (temp_data_dir / "ADSL.Rds").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["datasets_found"][0]["name"] == "ADSL"

    def test_discover_multiple_adam_in_filename(self, temp_data_dir):
        """Test files with multiple ADaM names (should extract the first valid one)."""
        # Edge case: filename mentions multiple ADaM datasets
        (temp_data_dir / "ADSL_vs_ADTTE_comparison.Rds").touch()

        from tealflow_mcp.tools.discovery import discover_datasets

        result = discover_datasets(temp_data_dir)

        assert result["status"] == "success"
        assert result["count"] == 1
        # Should extract the first ADaM dataset name found
        assert result["datasets_found"][0]["name"] in ["ADSL", "ADTTE"]


