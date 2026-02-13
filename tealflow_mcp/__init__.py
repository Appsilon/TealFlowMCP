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

__version__ = "0.1.3.post2"

from .core import PackageFilter, ResponseFormat
from .models import (
    CheckDatasetRequirementsInput,
    CheckShinyStartupInput,
    DiscoverDatasetsInput,
    GenerateDataLoadingInput,
    GenerateModuleCodeInput,
    GetAppTemplateInput,
    GetDatasetInfoInput,
    GetModuleDetailsInput,
    ListDatasetsInput,
    ListModulesInput,
    SearchModulesInput,
    SetupRenvEnvironmentInput,
    SnapshotRenvEnvironmentInput,
)

from .tools import (
    tealflow_check_dataset_requirements,
    tealflow_check_shiny_startup,
    tealflow_discover_datasets,
    tealflow_generate_data_loading,
    tealflow_generate_module_code,
    tealflow_get_agent_guidance,
    tealflow_get_app_template,
    tealflow_get_dataset_info,
    tealflow_get_module_details,
    tealflow_list_datasets,
    tealflow_list_modules,
    tealflow_search_modules_by_analysis,
    tealflow_setup_renv_environment,
    tealflow_snapshot_renv_environment,
)


def main() -> None:
    """Entry point for the tealflow-mcp console command.

    This function is called when running `tealflow-mcp` from the command line.
    It imports and runs the MCP server.
    """
    from .server import run_server

    run_server()


__all__ = [
    "CheckDatasetRequirementsInput",
    "CheckShinyStartupInput",
    "DiscoverDatasetsInput",
    "GenerateDataLoadingInput",
    "GenerateModuleCodeInput",
    "GetAppTemplateInput",
    "GetDatasetInfoInput",
    "GetModuleDetailsInput",
    "ListDatasetsInput",
    "ListModulesInput",
    "PackageFilter",
    "ResponseFormat",
    "SearchModulesInput",
    "SetupRenvEnvironmentInput",
    "SnapshotRenvEnvironmentInput",
    "__version__",
    "main",
    "tealflow_check_dataset_requirements",
    "tealflow_check_shiny_startup",
    "tealflow_discover_datasets",
    "tealflow_generate_data_loading",
    "tealflow_generate_module_code",
    "tealflow_get_agent_guidance",
    "tealflow_get_app_template",
    "tealflow_get_dataset_info",
    "tealflow_get_module_details",
    "tealflow_list_datasets",
    "tealflow_list_modules",
    "tealflow_search_modules_by_analysis",
    "tealflow_setup_renv_environment",
    "tealflow_snapshot_renv_environment",
]
