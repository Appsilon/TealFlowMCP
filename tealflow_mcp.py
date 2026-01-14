#!/usr/bin/env python3
"""
Teal Flow MCP Server - Entry Point

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

from tealflow_mcp import (
    CheckDatasetRequirementsInput,
    GenerateModuleCodeInput,
    GetAppTemplateInput,
    GetModuleDetailsInput,
    ListDatasetsInput,
    ListModulesInput,
    PackageFilter,
    ResponseFormat,
    SearchModulesInput,
    tealflow_check_dataset_requirements,
    tealflow_generate_module_code,
    tealflow_get_app_template,
    tealflow_get_module_details,
    tealflow_list_datasets,
    tealflow_list_modules,
    tealflow_search_modules_by_analysis,
)

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("tealflow_mcp")


# ============================================================================
# Tool Registration
# ============================================================================


@mcp.tool(
    name="tealflow_list_modules",
    annotations={
        "title": "List Teal Modules",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_modules_tool(
    package: str = "all",
    category: str | None = None,
    response_format: str = "markdown"
) -> str:
    """
    List all available Teal modules with their descriptions and dataset requirements.
    
    Args:
        package (str, optional): Filter by package - 'clinical', 'general', or 'all'. Defaults to 'all'.
        category (str, optional): Filter by category (e.g., 'graphics', 'tables', 'analysis'). Defaults to None.
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: List of modules in the specified format.
    """
    params = ListModulesInput(
        package=PackageFilter(package),
        category=category,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_list_modules(params)


@mcp.tool(
    name="tealflow_get_module_details",
    annotations={
        "title": "Get Module Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_module_details_tool(
    module_name: str,
    response_format: str = "markdown"
) -> str:
    """
    Get comprehensive details about a specific Teal module including all parameters.
    
    Args:
        module_name (str, required): Name of the module (e.g., 'tm_g_km', 'tm_t_coxreg', 'tm_g_scatterplot').
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: Detailed module information in the specified format.
    """
    params = GetModuleDetailsInput(
        module_name=module_name,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_get_module_details(params)


@mcp.tool(
    name="tealflow_search_modules_by_analysis",
    annotations={
        "title": "Search Modules by Analysis Type",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def search_modules_tool(
    analysis_type: str,
    response_format: str = "markdown"
) -> str:
    """
    Search for Teal modules that perform a specific type of analysis.
    
    Args:
        analysis_type (str, required): Type of analysis to search for (e.g., 'survival', 'kaplan-meier', 'forest plot', 'cox regression', 'scatter plot').
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: Matching modules in the specified format.
    """
    params = SearchModulesInput(
        analysis_type=analysis_type,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_search_modules_by_analysis(params)


@mcp.tool(
    name="tealflow_check_dataset_requirements",
    annotations={
        "title": "Check Dataset Requirements",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def check_dataset_requirements_tool(
    module_name: str,
    available_datasets: list[str] | None = None,
    response_format: str = "markdown"
) -> str:
    """
    Check if required datasets are available for a specific module.
    
    Args:
        module_name (str, required): Name of the module to check dataset requirements for.
        available_datasets (list[str], optional): List of available dataset names. Defaults to Flow's standard datasets: ['ADSL', 'ADTTE', 'ADRS', 'ADQS', 'ADAE'].
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: Dataset compatibility information in the specified format.
    """
    params = CheckDatasetRequirementsInput(
        module_name=module_name,
        available_datasets=available_datasets,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_check_dataset_requirements(params)


@mcp.tool(
    name="tealflow_list_datasets",
    annotations={
        "title": "List Available Datasets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def list_datasets_tool(
    response_format: str = "markdown"
) -> str:
    """
    List available clinical trial datasets in the Flow project.
    
    Args:
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: List of available datasets in the specified format.
    """
    params = ListDatasetsInput(
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_list_datasets(params)


@mcp.tool(
    name="tealflow_get_app_template",
    annotations={
        "title": "Get Teal App Template",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_app_template_tool(
    response_format: str = "markdown"
) -> str:
    """
    Get the Teal application template as a starting point for building apps.
    
    Args:
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.
    
    Returns:
        str: Teal application template in the specified format.
    """
    params = GetAppTemplateInput(
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_get_app_template(params)


@mcp.tool(
    name="tealflow_generate_module_code",
    annotations={
        "title": "Generate Teal Module Code",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def generate_module_code_tool(
    module_name: str,
    parameters: dict[str, any] | None = None,
    include_comments: bool = True
) -> str:
    """
    Generate R code for adding a module to a Teal application.
    
    Args:
        module_name (str, required): Name of the module to generate code for.
        parameters (dict[str, Any], optional): Optional parameter overrides as JSON object. Defaults to None.
        include_comments (bool, optional): Whether to include explanatory comments in the generated code. Defaults to True.
    
    Returns:
        str: Generated R code for the specified module.
    """
    params = GenerateModuleCodeInput(
        module_name=module_name,
        parameters=parameters,
        include_comments=include_comments
    )
    return await tealflow_generate_module_code(params)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
