"""
Tests for flexible dataset type support (BDS_DATASET, BDS_CONTINUOUS, BDS_BINARY).
"""

import pytest

from tealflow_mcp.core.enums import ResponseFormat
from tealflow_mcp.models import CheckDatasetRequirementsInput
from tealflow_mcp.tools.other_tools import tealflow_check_dataset_requirements


@pytest.mark.asyncio
class TestFlexibleDatasetTypes:
    """Test flexible dataset type matching in compatibility checking."""

    async def test_ancova_matches_adlb(self):
        """tm_t_ancova should match ADLB as BDS_CONTINUOUS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result
        assert "ADLB" in result

    async def test_ancova_matches_advs(self):
        """tm_t_ancova should match ADVS as BDS_CONTINUOUS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADVS"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result
        assert "ADVS" in result

    async def test_ancova_matches_adqs(self):
        """tm_t_ancova should match ADQS as BDS_CONTINUOUS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADQS"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result
        assert "ADQS" in result

    async def test_ancova_missing_bds(self):
        """tm_t_ancova should be incompatible without BDS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADAE"],  # ADAE is not BDS
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": false' in result
        assert "BDS_CONTINUOUS" in result

    async def test_mmrm_matches_multiple_bds(self):
        """tm_a_mmrm should match any BDS_CONTINUOUS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_a_mmrm",
            available_datasets=["ADSL", "ADLB", "ADVS", "ADQS"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result
        # Should show matched datasets
        assert "ADLB" in result or "ADVS" in result or "ADQS" in result

    async def test_gee_matches_any_bds(self):
        """tm_a_gee should match any BDS dataset (flexible for binary or continuous)."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_a_gee",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result

    async def test_summary_matches_any_bds(self):
        """tm_t_summary should match any BDS dataset."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_summary",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result

    async def test_specific_dataset_still_works(self):
        """Modules with specific dataset requirements still work."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_g_km",  # Requires ADTTE specifically
            available_datasets=["ADSL", "ADTTE"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": true' in result

    async def test_specific_dataset_missing(self):
        """Modules requiring specific datasets fail without them."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_g_km",  # Requires ADTTE specifically
            available_datasets=["ADSL", "ADLB"],  # ADLB doesn't match ADTTE
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"compatible": false' in result
        assert "ADTTE" in result

    async def test_markdown_format_shows_typical_datasets(self):
        """Markdown format should show typical datasets for flexible types."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.MARKDOWN,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert "✅" in result
        assert "Compatible" in result
        assert "Typical Datasets" in result or "ADLB" in result

    async def test_markdown_shows_guidance_for_missing_bds(self):
        """Markdown should provide helpful guidance for missing BDS datasets."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADAE"],
            response_format=ResponseFormat.MARKDOWN,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert "❌" in result
        assert "BDS_CONTINUOUS" in result
        assert "tealflow_get_dataset_info" in result  # Should suggest using this tool

    async def test_json_includes_matched_datasets(self):
        """JSON response should include matched flexible datasets."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADLB", "ADVS"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"matched_datasets"' in result
        assert '"BDS_CONTINUOUS"' in result

    async def test_typical_datasets_field_present(self):
        """Response should include typical_datasets field for flexible modules."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"typical_datasets"' in result
        # Should include at least one of the typical datasets
        assert any(ds in result for ds in ["ADLB", "ADVS", "ADQS"])

    async def test_dataset_requirements_details(self):
        """Response should include dataset requirements details."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_t_ancova",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"dataset_requirements"' in result
        assert "BDS_CONTINUOUS" in result

    async def test_notes_field_for_modules_with_notes(self):
        """Modules with notes should include them in response."""
        params = CheckDatasetRequirementsInput(
            module_name="tm_a_gee",
            available_datasets=["ADSL", "ADLB"],
            response_format=ResponseFormat.JSON,
        )
        result = await tealflow_check_dataset_requirements(params)
        assert '"notes"' in result
        # GEE has note about logistic vs linear regression
        assert "logistic" in result.lower() or "regression" in result.lower()
