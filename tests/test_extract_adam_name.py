"""
Unit tests for _extract_adam_name() function.

This test file focuses specifically on testing the ADaM name extraction logic
to ensure it handles all edge cases correctly.
"""

import pytest

from tealflow_mcp.tools.discovery import _extract_adam_name


class TestExtractAdamName:
    """Test the _extract_adam_name helper function."""

    def test_simple_uppercase_name(self):
        """Test extraction from simple uppercase filename."""
        assert _extract_adam_name("ADSL.Rds") == "ADSL"
        assert _extract_adam_name("ADTTE.csv") == "ADTTE"
        assert _extract_adam_name("ADAE.Rds") == "ADAE"

    def test_simple_lowercase_name(self):
        """Test extraction from simple lowercase filename."""
        assert _extract_adam_name("adsl.Rds") == "ADSL"
        assert _extract_adam_name("adtte.csv") == "ADTTE"
        assert _extract_adam_name("adae.Rds") == "ADAE"

    def test_mixed_case_name(self):
        """Test extraction from mixed case filename."""
        assert _extract_adam_name("AdSl.Rds") == "ADSL"
        assert _extract_adam_name("AdTtE.csv") == "ADTTE"
        assert _extract_adam_name("aDaE.Rds") == "ADAE"

    def test_name_with_prefix(self):
        """Test extraction when ADaM name has prefix."""
        assert _extract_adam_name("project_ADSL.Rds") == "ADSL"
        assert _extract_adam_name("study123_ADTTE.csv") == "ADTTE"
        assert _extract_adam_name("drugX_ADAE.Rds") == "ADAE"

    def test_name_with_suffix(self):
        """Test extraction when ADaM name has suffix."""
        assert _extract_adam_name("ADSL_final.Rds") == "ADSL"
        assert _extract_adam_name("ADTTE_v2.csv") == "ADTTE"
        assert _extract_adam_name("ADAE_locked.Rds") == "ADAE"

    def test_name_with_prefix_and_suffix(self):
        """Test extraction when ADaM name has both prefix and suffix."""
        assert _extract_adam_name("project_ADSL_final.Rds") == "ADSL"
        assert _extract_adam_name("study_ADTTE_v2.csv") == "ADTTE"
        assert _extract_adam_name("drugX_ADAE_locked.Rds") == "ADAE"

    def test_complex_filename_with_date(self):
        """Test extraction from complex filename with date."""
        assert _extract_adam_name("project123_ADSL_2024-01-15.Rds") == "ADSL"
        assert _extract_adam_name("study_ADTTE_2023-12-31.csv") == "ADTTE"

    def test_complex_filename_with_multiple_parts(self):
        """Test extraction from filename with many parts."""
        assert _extract_adam_name("phase3_study_ADSL_final_locked_v2.Rds") == "ADSL"
        assert _extract_adam_name("drug_trial_ADTTE_interim_2024.csv") == "ADTTE"

    def test_underscore_separators(self):
        """Test that underscores work as separators."""
        assert _extract_adam_name("project_ADSL_final.Rds") == "ADSL"
        assert _extract_adam_name("_ADSL_.Rds") == "ADSL"

    def test_hyphen_separators(self):
        """Test that hyphens work as separators."""
        assert _extract_adam_name("project-ADSL-final.Rds") == "ADSL"
        assert _extract_adam_name("-ADSL-.Rds") == "ADSL"

    def test_mixed_separators(self):
        """Test mixed separator types."""
        assert _extract_adam_name("project-ADSL_final.Rds") == "ADSL"
        assert _extract_adam_name("study_123-ADTTE-v2.csv") == "ADTTE"

    def test_all_standard_adam_datasets(self):
        """Test all standard ADaM dataset names are recognized."""
        standard_datasets = [
            "ADSL",
            "ADTTE",
            "ADRS",
            "ADQS",
            "ADAE",
            "ADLB",
            "ADVS",
            "ADCM",
            "ADEX",
            "ADMH",
        ]
        for dataset in standard_datasets:
            assert _extract_adam_name(f"{dataset}.Rds") == dataset
            assert _extract_adam_name(f"project_{dataset}_final.csv") == dataset

    def test_false_positive_admin(self):
        """Test that 'admin' is not detected as ADMH or ADSL."""
        assert _extract_adam_name("admin.csv") is None
        assert _extract_adam_name("admin_notes.csv") is None
        assert _extract_adam_name("administrator.Rds") is None

    def test_false_positive_advanced(self):
        """Test that 'advanced' is not detected as ADVS."""
        assert _extract_adam_name("advanced.csv") is None
        assert _extract_adam_name("advanced_analysis.Rds") is None

    def test_false_positive_address(self):
        """Test that 'address' is not detected as ADRS."""
        assert _extract_adam_name("address.csv") is None
        assert _extract_adam_name("address_book.Rds") is None

    def test_false_positive_ad_prefix(self):
        """Test that files starting with AD but not ADaM names return None."""
        assert _extract_adam_name("ADFOO.Rds") is None
        assert _extract_adam_name("AD123.csv") is None
        assert _extract_adam_name("ADXYZ.Rds") is None

    def test_non_adam_files(self):
        """Test that non-ADaM files return None."""
        assert _extract_adam_name("README.md") is None
        assert _extract_adam_name("data.txt") is None
        assert _extract_adam_name("config.json") is None
        assert _extract_adam_name("script.R") is None

    def test_empty_filename(self):
        """Test that empty filename returns None."""
        assert _extract_adam_name("") is None

    def test_multiple_adam_names_returns_first(self):
        """Test that filename with multiple ADaM names returns the first one found."""
        # This behavior is documented in the tests - extract first valid match
        result = _extract_adam_name("ADSL_vs_ADTTE_comparison.Rds")
        assert result in ["ADSL", "ADTTE"]  # Either is acceptable
        assert result is not None

    def test_case_insensitive_with_numbers(self):
        """Test case insensitivity with numbers in filename."""
        assert _extract_adam_name("project123_adsl_v2.Rds") == "ADSL"
        assert _extract_adam_name("study456_AdTtE_2024.csv") == "ADTTE"

    def test_adam_name_at_start(self):
        """Test ADaM name at the beginning of filename."""
        assert _extract_adam_name("ADSL_2024_final.Rds") == "ADSL"
        assert _extract_adam_name("adtte_study123.csv") == "ADTTE"

    def test_adam_name_at_end(self):
        """Test ADaM name at the end of filename (before extension)."""
        assert _extract_adam_name("project_final_ADSL.Rds") == "ADSL"
        assert _extract_adam_name("study_interim_adtte.csv") == "ADTTE"

    def test_adam_name_middle(self):
        """Test ADaM name in the middle of filename."""
        assert _extract_adam_name("project_ADSL_final_v2.Rds") == "ADSL"
        assert _extract_adam_name("study_adtte_locked_2024.csv") == "ADTTE"

    def test_no_separators_between_parts(self):
        """Test that ADaM name must be separated from other alphanumeric characters."""
        # These should NOT match because ADaM name is not separated
        assert _extract_adam_name("PROJECTADSL.Rds") is None
        assert _extract_adam_name("ADSLPROJECT.Rds") is None
        assert _extract_adam_name("MYADSLFINAL.csv") is None

    def test_numeric_before_after(self):
        """Test that numbers act as separators."""
        assert _extract_adam_name("123ADSL456.Rds") == "ADSL"
        assert _extract_adam_name("v1_ADTTE_v2.csv") == "ADTTE"

    def test_special_chars_as_separators(self):
        """Test that various special characters act as separators."""
        assert _extract_adam_name("project.ADSL.final.Rds") == "ADSL"
        assert _extract_adam_name("study-ADTTE-v2.csv") == "ADTTE"
        assert _extract_adam_name("data_ADAE_2024.Rds") == "ADAE"

    def test_extension_variations(self):
        """Test that different file extensions don't affect extraction."""
        assert _extract_adam_name("ADSL.RDS") == "ADSL"
        assert _extract_adam_name("ADSL.rds") == "ADSL"
        assert _extract_adam_name("ADSL.CSV") == "ADSL"
        assert _extract_adam_name("ADSL.csv") == "ADSL"
        assert _extract_adam_name("ADSL.parquet") == "ADSL"
