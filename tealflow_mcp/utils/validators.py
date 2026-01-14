"""
Validation utilities for Teal Flow MCP Server.
"""

from difflib import get_close_matches

from ..data import _get_clinical_modules, _get_general_modules


def _fuzzy_match_module(module_name: str, all_modules: list[str]) -> str | None:
    """Find closest matching module name for typos."""
    matches = get_close_matches(module_name, all_modules, n=1, cutoff=0.6)
    return matches[0] if matches else None


def _validate_module_exists(module_name: str) -> tuple[bool, str | None, str | None]:
    """
    Validate if a module exists and return its package.

    Returns:
        (exists, package, suggestion)
    """
    clinical_data = _get_clinical_modules()
    general_data = _get_general_modules()

    clinical_modules = clinical_data.get("modules", {})
    general_modules = general_data.get("modules", {})

    if module_name in clinical_modules:
        return (True, "clinical", None)
    if module_name in general_modules:
        return (True, "general", None)
    # Try fuzzy matching
    all_modules = list(clinical_modules.keys()) + list(general_modules.keys())
    suggestion = _fuzzy_match_module(module_name, all_modules)
    return (False, None, suggestion)
