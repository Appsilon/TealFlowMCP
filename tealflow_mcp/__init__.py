"""
Teal Flow MCP Server

This MCP server provides tools to discover, understand, and generate Teal R Shiny
applications for clinical trial data analysis. It enables LLMs to work with
teal.modules.clinical and teal.modules.general packages programmatically.

The server helps with:
- Discovering available Teal modules
- Understanding module requirements and parameters
- Checking dataset compatibility
- Searching modules by analysis type
- Generating R code for Teal apps
"""

from .core import PackageFilter, ResponseFormat
from .models import (
    CheckDatasetRequirementsInput,
    DiscoverDatasetsInput,
    CheckShinyStartupInput,
    GenerateModuleCodeInput,
    GetAppTemplateInput,
    GetModuleDetailsInput,
    ListDatasetsInput,
    ListModulesInput,
    SearchModulesInput,
    SetupRenvEnvironmentInput,
)

from .tools import (
    tealflow_check_dataset_requirements,
    tealflow_discover_datasets,
    tealflow_check_shiny_startup,
    tealflow_generate_module_code,
    tealflow_get_agent_guidance,
    tealflow_get_app_template,
    tealflow_get_module_details,
    tealflow_list_datasets,
    tealflow_list_modules,
    tealflow_search_modules_by_analysis,
    tealflow_setup_renv_environment,
)

__all__ = [
    "CheckDatasetRequirementsInput",
    "DiscoverDatasetsInput",
    "CheckShinyStartupInput",
    "GenerateModuleCodeInput",
    "GetAppTemplateInput",
    "GetModuleDetailsInput",
    "ListDatasetsInput",
    "ListModulesInput",
    "PackageFilter",
    "ResponseFormat",
    "SearchModulesInput",
    "SetupRenvEnvironmentInput",
    "tealflow_check_dataset_requirements",
    "tealflow_discover_datasets",
    "tealflow_check_shiny_startup",
    "tealflow_generate_module_code",
    "tealflow_get_agent_guidance",
    "tealflow_get_app_template",
    "tealflow_get_module_details",
    "tealflow_list_datasets",
    "tealflow_list_modules",
    "tealflow_search_modules_by_analysis",
    "tealflow_setup_renv_environment",
]
