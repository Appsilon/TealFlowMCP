"""
Enumerations for Teal Flow MCP Server.
"""

from enum import Enum


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class PackageFilter(str, Enum):
    """Teal package filter options."""

    ALL = "all"
    CLINICAL = "clinical"
    GENERAL = "general"
