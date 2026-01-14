"""
Data loading functions for Teal Flow MCP Server.
"""

import json
from typing import Any

from ..core.constants import WORKSPACE_DIR

# Global data cache
_MODULE_DATA_CACHE: dict[str, Any] = {}


def _load_json_file(filename: str) -> dict[str, Any]:
    """Load and cache JSON data files from workspace."""
    if filename not in _MODULE_DATA_CACHE:
        file_path = WORKSPACE_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required data file not found: {filename}")

        with open(file_path) as f:
            _MODULE_DATA_CACHE[filename] = json.load(f)

    return _MODULE_DATA_CACHE[filename]


def _get_clinical_modules() -> dict[str, Any]:
    """Get clinical modules data."""
    data = _load_json_file("teal_modules_clinical_dataset_requirements.json")
    return data.get("teal.modules.clinical_simple", {})


def _get_clinical_module_requirements() -> dict[str, Any]:
    """Get detailed clinical module requirements."""
    data = _load_json_file("teal_modules_clinical_modules_requirements.json")
    return data.get("teal.modules.clinical_dataset_requirements", {})


def _get_general_modules() -> dict[str, Any]:
    """Get general modules data."""
    data = _load_json_file("teal_modules_general_modules_requirements.json")
    return data.get("teal.modules.general_detailed", {})


def _get_default_datasets() -> list[str]:
    """Get the default datasets available in Flow."""
    return ["ADSL", "ADTTE", "ADRS", "ADQS", "ADAE"]


def _get_clinical_by_analysis_type() -> dict[str, Any]:
    """Get clinical modules organized by analysis type."""
    data = _load_json_file("teal_modules_clinical_by_analysis_type.json")
    return data.get("teal.modules.clinical_by_analysis_type", {})


def _get_general_by_analysis_type() -> dict[str, Any]:
    """Get general modules organized by analysis type."""
    data = _load_json_file("teal_modules_general_by_analysis_type.json")
    return data.get("teal.modules.general_by_analysis_type", {})
