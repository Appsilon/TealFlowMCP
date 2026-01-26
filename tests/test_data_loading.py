"""
Unit tests for data loading code generation functionality.

Tests the generation of R code that loads ADaM datasets and creates teal_data objects.
"""

import pytest
import json


class TestDataLoadingCodeGeneration:
    """Test data loading code generation functionality."""

    def test_generate_rds_only(self):
        """Test generating code for only RDS files."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADTTE",
                "path": "/home/user/project/data/ADTTE.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Check structure
        assert "library(teal)" in result
        assert 'ADSL <- readRDS("/home/user/project/data/ADSL.Rds")' in result
        assert 'ADTTE <- readRDS("/home/user/project/data/ADTTE.Rds")' in result
        assert "data <- teal_data(" in result
        assert "ADSL = ADSL," in result
        assert "ADTTE = ADTTE" in result  # Last one without comma
        assert 'join_keys = default_cdisc_join_keys[c("ADSL", "ADTTE")]' in result

    def test_generate_csv_only(self):
        """Test generating code for only CSV files."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.csv",
                "format": "csv",
                "is_standard_adam": True,
            },
            {
                "name": "ADAE",
                "path": "/home/user/project/data/ADAE.csv",
                "format": "csv",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Check CSV loading
        assert 'ADSL <- read.csv("/home/user/project/data/ADSL.csv", stringsAsFactors = FALSE)' in result
        assert 'ADAE <- read.csv("/home/user/project/data/ADAE.csv", stringsAsFactors = FALSE)' in result
        assert "data <- teal_data(" in result

    def test_generate_mixed_formats(self):
        """Test generating code with both RDS and CSV files."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADTTE",
                "path": "/home/user/project/data/ADTTE.csv",
                "format": "csv",
                "is_standard_adam": True,
            },
            {
                "name": "ADAE",
                "path": "/home/user/project/data/ADAE.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Check mixed formats
        assert 'ADSL <- readRDS("/home/user/project/data/ADSL.Rds")' in result
        assert 'ADTTE <- read.csv("/home/user/project/data/ADTTE.csv", stringsAsFactors = FALSE)' in result
        assert 'ADAE <- readRDS("/home/user/project/data/ADAE.Rds")' in result

    def test_generate_standard_adam_only(self):
        """Test that standard ADaM datasets use default_cdisc_join_keys."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADTTE",
                "path": "/home/user/project/data/ADTTE.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADRS",
                "path": "/home/user/project/data/ADRS.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Should use default join keys
        assert 'join_keys = default_cdisc_join_keys[c("ADSL", "ADRS", "ADTTE")]' in result
        assert "WARNING" not in result

    def test_generate_with_non_standard(self):
        """Test that non-standard datasets trigger warning comment."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "CUSTOM",
                "path": "/home/user/project/data/CUSTOM.Rds",
                "format": "Rds",
                "is_standard_adam": False,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Should have warning
        assert "WARNING: Non-standard datasets detected" in result
        assert "You may need to configure join_keys manually" in result
        assert "default_cdisc_join_keys" not in result

    def test_generate_empty_list(self):
        """Test error handling for empty dataset list."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = []

        with pytest.raises(ValueError) as exc_info:
            generate_data_loading_code(datasets, "/home/user/project/data")

        assert "No datasets provided" in str(exc_info.value)

    def test_generate_sorts_by_name(self):
        """Test that datasets are sorted alphabetically in output."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADTTE",
                "path": "/home/user/project/data/ADTTE.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADSL",
                "path": "/home/user/project/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADRS",
                "path": "/home/user/project/data/ADRS.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Find positions of dataset loading lines
        adsl_pos = result.index("ADSL <- readRDS")
        adrs_pos = result.index("ADRS <- readRDS")
        adtte_pos = result.index("ADTTE <- readRDS")

        # Should be in alphabetical order
        assert adsl_pos < adrs_pos < adtte_pos

        # Check join_keys order (should also be sorted)
        assert 'join_keys = default_cdisc_join_keys[c("ADSL", "ADRS", "ADTTE")]' in result

    def test_generate_absolute_paths(self):
        """Test that absolute paths are preserved correctly."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/my-project/workspace/datasets/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Check exact path preservation
        assert (
            'ADSL <- readRDS("/home/user/my-project/workspace/datasets/ADSL.Rds")'
            in result
        )

    def test_generate_all_standard_datasets(self):
        """Test generation with all 10 standard ADaM datasets."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {"name": "ADSL", "path": "/data/ADSL.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADTTE", "path": "/data/ADTTE.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADRS", "path": "/data/ADRS.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADQS", "path": "/data/ADQS.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADAE", "path": "/data/ADAE.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADLB", "path": "/data/ADLB.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADVS", "path": "/data/ADVS.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADCM", "path": "/data/ADCM.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADEX", "path": "/data/ADEX.Rds", "format": "Rds", "is_standard_adam": True},
            {"name": "ADMH", "path": "/data/ADMH.Rds", "format": "Rds", "is_standard_adam": True},
        ]

        result = generate_data_loading_code(datasets)

        # All should be loaded
        for ds in datasets:
            assert f'{ds["name"]} <- readRDS' in result

        # Should use default join keys
        assert "default_cdisc_join_keys" in result
        assert "WARNING" not in result

    def test_generate_windows_paths(self):
        """Test generation with Windows-style absolute paths."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "C:\\Users\\user\\project\\data\\ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        # Windows paths should be preserved (backslashes might be escaped in R strings)
        assert "ADSL <- readRDS" in result
        assert "C:" in result

    def test_generate_complex_filenames(self):
        """Test that complex filenames work correctly (path should contain them)."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/home/user/data/project123_ADSL_2024-01-15.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets, "/home/user/data")

        # Full filename should be in path
        assert 'ADSL <- readRDS("/home/user/data/project123_ADSL_2024-01-15.Rds")' in result

    def test_generate_code_structure(self):
        """Test the overall structure of generated code."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
            {
                "name": "ADTTE",
                "path": "/data/ADTTE.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)
        lines = result.split("\n")

        # Check structure
        assert lines[0] == "library(teal)"
        assert lines[1] == ""
        assert any("ADSL <- readRDS" in line for line in lines)
        assert any("## Data reproducible code ----" in line for line in lines)
        assert any("data <- teal_data(" in line for line in lines)

    def test_generate_single_dataset(self):
        """Test generation with a single dataset."""
        from tealflow_mcp.tools.data_loading import generate_data_loading_code

        datasets = [
            {
                "name": "ADSL",
                "path": "/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        result = generate_data_loading_code(datasets)

        assert 'ADSL <- readRDS("/data/ADSL.Rds")' in result
        assert "ADSL = ADSL" in result  # No comma after single dataset
        assert 'join_keys = default_cdisc_join_keys[c("ADSL")]' in result


class TestDataLoadingToolWrapper:
    """Test the MCP tool wrapper for data loading generation."""

    async def test_tool_markdown_format(self):
        """Test tool wrapper with markdown output format."""
        from tealflow_mcp.tools.data_loading import tealflow_generate_data_loading
        from tealflow_mcp.models.input_models import GenerateDataLoadingInput
        from tealflow_mcp.core.enums import ResponseFormat

        datasets = [
            {
                "name": "ADSL",
                "path": "/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        params = GenerateDataLoadingInput(
            datasets=datasets,
            response_format=ResponseFormat.MARKDOWN,
        )

        result = await tealflow_generate_data_loading(params)

        # Should be markdown formatted
        assert "# Data Loading Code" in result
        assert "```r" in result
        assert "```" in result
        assert "## Usage" in result

    async def test_tool_json_format(self):
        """Test tool wrapper with JSON output format."""
        from tealflow_mcp.tools.data_loading import tealflow_generate_data_loading
        from tealflow_mcp.models.input_models import GenerateDataLoadingInput
        from tealflow_mcp.core.enums import ResponseFormat

        datasets = [
            {
                "name": "ADSL",
                "path": "/data/ADSL.Rds",
                "format": "Rds",
                "is_standard_adam": True,
            },
        ]

        params = GenerateDataLoadingInput(
            datasets=datasets,
            response_format=ResponseFormat.JSON,
        )

        result = await tealflow_generate_data_loading(params)

        # Should be valid JSON
        parsed = json.loads(result)
        assert "code" in parsed
        assert "datasets" in parsed
        assert "file_path" in parsed
        assert parsed["file_path"] == "data/data.R"
        assert "ADSL" in parsed["datasets"]

    async def test_tool_empty_datasets_error(self):
        """Test tool error handling for empty datasets."""
        from tealflow_mcp.tools.data_loading import tealflow_generate_data_loading
        from tealflow_mcp.models.input_models import GenerateDataLoadingInput

        params = GenerateDataLoadingInput(
            datasets=[],
        )

        result = await tealflow_generate_data_loading(params)

        # Should return error message
        assert "Error" in result or "error" in result

    async def test_tool_with_discovery_output(self):
        """Test tool integration with actual discovery output format."""
        from tealflow_mcp.tools.data_loading import tealflow_generate_data_loading
        from tealflow_mcp.models.input_models import GenerateDataLoadingInput

        # Simulate discovery output
        discovery_output = {
            "status": "success",
            "data_directory": "/home/user/data",
            "datasets_found": [
                {
                    "name": "ADSL",
                    "path": "/home/user/data/ADSL.Rds",
                    "format": "Rds",
                    "is_standard_adam": True,
                    "size_bytes": 25357,
                    "readable": True,
                },
                {
                    "name": "ADTTE",
                    "path": "/home/user/data/ADTTE.Rds",
                    "format": "Rds",
                    "is_standard_adam": True,
                    "size_bytes": 71198,
                    "readable": True,
                },
            ],
            "count": 2,
            "supported_formats": ["Rds", "csv"],
            "warnings": [],
        }

        params = GenerateDataLoadingInput(
            datasets=discovery_output["datasets_found"],
        )

        result = await tealflow_generate_data_loading(params)

        # Should generate valid code
        assert "library(teal)" in result
        assert "ADSL <- readRDS" in result
        assert "ADTTE <- readRDS" in result
