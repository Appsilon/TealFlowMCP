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
async def list_modules_tool(params: ListModulesInput) -> str:
    """List all available Teal modules with their descriptions and dataset requirements."""
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
async def get_module_details_tool(params: GetModuleDetailsInput) -> str:
    """Get comprehensive details about a specific Teal module including all parameters."""
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
async def search_modules_tool(params: SearchModulesInput) -> str:
    """Search for Teal modules that perform a specific type of analysis."""
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
async def check_dataset_requirements_tool(params: CheckDatasetRequirementsInput) -> str:
    """Check if required datasets are available for a specific module."""
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
async def list_datasets_tool(params: ListDatasetsInput) -> str:
    """List available clinical trial datasets in the Flow project."""
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
async def get_app_template_tool(params: GetAppTemplateInput) -> str:
    """Get the Teal application template as a starting point for building apps."""
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
async def generate_module_code_tool(params: GenerateModuleCodeInput) -> str:
    """Generate R code for adding a module to a Teal application."""
    return await tealflow_generate_module_code(params)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
