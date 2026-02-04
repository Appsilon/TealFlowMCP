"""
Unit tests for R helper utilities.

Tests the helper functions for interacting with R/Rscript.
"""

import pytest


class TestGetRHelp:
    """Test _get_r_help function."""

    def test_get_help_base_function(self):
        """Test getting help for a base R function."""
        from tealflow_mcp.utils import _get_r_help

        help_text = _get_r_help("mean")

        # Should contain function name and description
        assert "mean" in help_text.lower()
        # Should contain some documentation
        assert len(help_text) > 50

    def test_get_help_with_package(self):
        """Test getting help for a function from a specific package."""
        from tealflow_mcp.utils import _get_r_help

        help_text = _get_r_help("mean", package="base")

        # Should contain function name
        assert "mean" in help_text.lower()
        assert len(help_text) > 50

    def test_get_help_stats_function(self):
        """Test getting help for a stats package function."""
        from tealflow_mcp.utils import _get_r_help

        help_text = _get_r_help("lm")

        # Should contain function name and description
        assert "lm" in help_text.lower()
        # Should mention linear models or fitting
        assert "linear" in help_text.lower() or "model" in help_text.lower()

    def test_get_help_nonexistent_function(self):
        """Test behavior when function doesn't exist."""
        from tealflow_mcp.utils import _get_r_help

        with pytest.raises(ValueError) as exc_info:
            _get_r_help("nonexistent_function_xyz123")

        # Should have meaningful error message
        assert "not found" in str(exc_info.value).lower()

    def test_get_help_nonexistent_package(self):
        """Test behavior when package doesn't exist."""
        from tealflow_mcp.utils import _get_r_help

        with pytest.raises(ValueError) as exc_info:
            _get_r_help("mean", package="nonexistent_package_xyz")

        # Should have meaningful error message
        assert "package" in str(exc_info.value).lower()

    def test_get_help_function_not_in_package(self):
        """Test when function exists but not in specified package."""
        from tealflow_mcp.utils import _get_r_help

        with pytest.raises(ValueError) as exc_info:
            # mean is in base, not in stats
            _get_r_help("mean", package="stats")

        assert "not found" in str(exc_info.value).lower()
