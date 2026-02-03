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
    DiscoverDatasetsInput,
    CheckShinyStartupInput,
    GenerateDataLoadingInput,
    GenerateModuleCodeInput,
    GetAppTemplateInput,
    GetModuleDetailsInput,
    ListDatasetsInput,
    ListModulesInput,
    PackageFilter,
    ResponseFormat,
    SearchModulesInput,
    SetupRenvEnvironmentInput,
    SnapshotRenvEnvironmentInput,
    tealflow_get_agent_guidance,
    tealflow_check_dataset_requirements,
    tealflow_discover_datasets,
    tealflow_check_shiny_startup,
    tealflow_generate_data_loading,
    tealflow_generate_module_code,
    tealflow_get_app_template,
    tealflow_get_module_details,
    tealflow_list_datasets,
    tealflow_list_modules,
    tealflow_search_modules_by_analysis,
    tealflow_setup_renv_environment,
    tealflow_snapshot_renv_environment,
)

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    "tealflow_mcp",
    instructions=(
        "⚠️ CRITICAL: Before assisting with ANY Teal-related task, you MUST call the "
        "'tealflow_agent_guidance' tool to retrieve comprehensive guidance. "
        "This includes: creating Teal apps, adding modules, implementing analyses, "
        "working with SAPs, or any clinical trial data analysis task. "
        "The guidance contains essential workflows, constraints, and best practices."
    )
)


# ============================================================================
# Prompt Registration
# ============================================================================


@mcp.tool(
    name="tealflow_agent_guidance",
    annotations={
        "title": "Get Agent Guidance",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def get_agent_guidance_tool() -> str:
    """
    Get comprehensive guidance for assisting users with Teal application development.

    ⚠️ IMPORTANT: This tool MUST be called FIRST whenever a user requests:
    - Creating a Teal application or Teal app
    - Adding Teal modules to an app
    - Building clinical trial analysis applications
    - Survival analysis, safety analysis, efficacy analysis, or any clinical data analysis
    - Working with Statistical Analysis Plans (SAP)
    - Understanding Teal modules or datasets
    - Any other Teal-related task

    This tool provides the complete agent usage guide that includes:
    - Your role and responsibilities as a Teal assistant
    - Available MCP tools and when to use them
    - Step-by-step workflow guidance for common scenarios
    - Teal framework knowledge (modules, datasets, architecture)
    - Important module constraints and special cases
    - Development philosophy and R code style guidelines
    - Best practices for agent behavior
    - Example workflows for common tasks

    The guidance ensures you:
    - Follow correct workflows for creating and modifying Teal apps
    - Use the right MCP tools in the right sequence
    - Verify dataset compatibility before suggesting modules
    - Generate properly structured R code
    - Provide complete, working solutions
    - Handle multi-step tasks with proper planning

    Usage:
        Always retrieve this guidance at the start of any Teal-related conversation
        to ensure you have the latest best practices, workflows, and constraints.

    Returns:
        str: Complete agent guidance document in markdown format with all necessary
             context, workflows, and best practices for assisting with Teal development.

    Examples:
        User: "I need to create a survival analysis app"
        → First action: Call this tool to get guidance
        → Then follow the workflow in the guidance to assist the user

        User: "Add a Kaplan-Meier module to my app"
        → First action: Call this tool to get guidance
        → Then use the appropriate MCP tools as directed in the guidance

        User: "Help me implement analyses from my SAP"
        → First action: Call this tool to get guidance
        → Then follow the SAP workflow described in the guidance
    """
    return await tealflow_get_agent_guidance()


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

    This tool helps discover what analysis modules are available in the Teal framework.
    Modules can be filtered by package (clinical vs general) and optionally by category.

    Clinical modules are designed for clinical trial reporting and work with ADaM datasets.
    General modules are for general-purpose data exploration and work with any data.frame.

    Args:
        package (str, optional): Filter by package - 'clinical', 'general', or 'all'. Defaults to 'all'.
        category (str, optional): Filter by category like 'graphics', 'tables', 'analysis'. Defaults to None.
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: List of modules with names, descriptions, and required datasets

        Markdown format:
            # Teal Modules (Package Name)

            ## module_name
            **Description**: Module description
            **Required Datasets**: ADSL, ADTTE (or "None")

        JSON format:
            {
                "modules": [
                    {
                        "name": "tm_g_km",
                        "description": "Kaplan-Meier Plot",
                        "required_datasets": ["ADSL", "ADTTE"]
                    }
                ],
                "count": 10
            }

    Examples:
        - List all clinical modules: package="clinical"
        - List graphics modules: category="graphics"
        - Get machine-readable list: response_format="json"
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

    This tool provides complete information about a module's required and optional
    parameters, their types, default values, and descriptions. Use this after
    discovering a module to understand how to configure it properly.

    Args:
        module_name (str, required): Name of the module (e.g., 'tm_g_km', 'tm_t_coxreg', 'tm_g_scatterplot').
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: Detailed module information including parameters, datasets, and usage

        Includes:
        - Module description
        - Required datasets
        - Required parameters (no defaults)
        - Optional parameters (with defaults)
        - Parameter types and constraints
        - Usage examples

    Error Handling:
        - Returns error if module not found
        - Suggests similar module names for typos
        - Provides guidance on correct module names

    Examples:
        - Get details for KM plot: module_name="tm_g_km"
        - Get Cox regression info: module_name="tm_t_coxreg"
        - Get JSON format: response_format="json"
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

    This tool helps find appropriate modules when you know what analysis you need
    but don't know which module to use. It uses structured analysis type categories
    combined with text search for comprehensive results.

    Args:
        analysis_type (str, required): Type of analysis to search for (e.g., 'survival', 'safety', 'efficacy', 'data exploration', 'visualization', 'kaplan-meier', 'forest plot', 'cox regression', 'scatter plot').
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: List of matching modules organized by relevance

        Includes:
        - Analysis category matches (structured)
        - Module names and descriptions
        - Required datasets
        - Category descriptions

    Predefined Analysis Categories:
        Clinical: survival_analysis, safety_analysis, efficacy_analysis,
                 descriptive_analysis, laboratory_analysis, patient_profiles
        General: data_exploration, statistical_analysis, visualization,
                data_quality, multivariate_analysis

    Examples:
        - Find survival analysis modules: analysis_type="survival"
        - Find safety modules: analysis_type="safety"
        - Find visualization modules: analysis_type="visualization"
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

    This tool validates whether you have all necessary datasets before attempting
    to use a module. It compares the module's dataset requirements against your
    available datasets and provides clear feedback.

    Args:
        module_name (str, required): Name of the module to check dataset requirements for.
        available_datasets (list[str], optional): List of available dataset names. Defaults to Flow's standard datasets: ['ADSL', 'ADTTE', 'ADRS', 'ADQS', 'ADAE'].
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: Compatibility report with status and missing datasets

        Includes:
        - Compatibility status (compatible/incompatible)
        - List of required datasets
        - List of missing datasets (if any)
        - Suggestions for alternatives

    Examples:
        - Check with defaults: module_name="tm_g_km"
        - Check with custom datasets: module_name="tm_g_km", available_datasets=["ADSL", "ADTTE", "ADLB"]
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

    This tool provides information about the standard ADaM datasets available
    for use with Teal clinical modules. These datasets follow CDISC standards
    for clinical trial data.

    Args:
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: List of datasets with descriptions and relationships

        Includes:
        - Dataset names (e.g., ADSL, ADTTE)
        - Descriptions
        - Usage information
        - Relationship to other datasets

    Examples:
        - List all datasets: (no parameters needed)
        - Get JSON format: response_format="json"
    """
    params = ListDatasetsInput(
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_list_datasets(params)


@mcp.tool(
    name="tealflow_discover_datasets",
    annotations={
        "title": "Discover ADaM Datasets",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def discover_datasets_tool(
    data_directory: str,
    file_formats: list[str] | None = None,
    pattern: str = "AD*",
    response_format: str = "markdown"
) -> str:
    """
    Discover ADaM datasets in a directory.

    This tool scans a directory for ADaM dataset files, identifies the dataset
    names, and collects metadata about each dataset. It handles complex filenames
    with project names, dates, and drug names, and normalizes dataset names to
    uppercase.

    **IMPORTANT**: This tool requires an **absolute path** to the dataset directory.
    Relative paths will not work correctly due to MCP server/client working directory differences.

    Args:
        data_directory (str): **Absolute path** to the directory containing dataset files.
                             Example: '/home/user/project/data/' or 'C:\\Users\\user\\project\\data\\'.
        file_formats (list[str], optional): List of file formats to include (e.g., ['Rds', 'csv']).
                                           If None, all supported formats are included. Defaults to None.
        pattern (str, optional): File pattern to match (default: 'AD*' for ADaM datasets). Defaults to 'AD*'.
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable.
                                        Defaults to 'markdown'.

    Returns:
        str: Discovery results with information about found datasets

        Includes:
        - List of discovered datasets with names, paths, and formats
        - Dataset metadata (size, readability, standard vs custom)
        - Summary statistics
        - Warnings about any issues

    Examples:
        - Discover datasets with absolute path: data_directory="/home/user/project/workspace/"
        - Discover with specific format: data_directory="/home/user/data/", file_formats=["Rds"]
        - Get JSON format: data_directory="/home/user/data/", response_format="json"

    Common Errors:
        - FileNotFoundError: Directory not found. Ensure you provide the full absolute path.
        - Relative paths like "data/" or "workspace/" will not work - use absolute paths.

    Note:
        This tool extracts ADaM dataset names from filenames, handling:
        - Complex filenames (e.g., "project123_ADSL_2024-01-15.Rds" → "ADSL")
        - Case variations (e.g., "adsl.Rds", "AdTtE.csv" → "ADSL", "ADTTE")
        - Multiple formats (.Rds, .csv, case-insensitive extensions)

        For best results, always ask the user for the complete absolute path to their dataset directory.
    """
    params = DiscoverDatasetsInput(
        data_directory=data_directory,
        file_formats=file_formats,
        pattern=pattern,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_discover_datasets(params)


@mcp.tool(
    name="tealflow_generate_data_loading",
    annotations={
        "title": "Generate Data Loading Code",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def generate_data_loading_tool(
    datasets: list[dict],
    project_directory: str | None = None,
    response_format: str = "markdown"
) -> str:
    """
    Generate R code for loading discovered datasets and creating a teal_data object.

    This tool generates complete R code that loads ADaM datasets from files and
    creates a teal_data object with appropriate join keys. It's designed to work
    seamlessly with the output from tealflow_discover_datasets.

    **IMPORTANT**: This tool requires the datasets list from tealflow_discover_datasets.
    Pass the 'datasets_found' array directly to this tool.

    **Path Handling**: If datasets are in the project directory, provide project_directory
    to generate relative paths. Otherwise, absolute paths will be used.

    Args:
        datasets (list[dict[str, Any]]): List of dataset dictionaries from discovery.
                                         Each dictionary must contain:
                                         - name: Dataset name (e.g., "ADSL")
                                         - path: Absolute path to dataset file
                                         - format: File format ("Rds" or "csv")
                                         - is_standard_adam: Whether it's a standard ADaM dataset
        project_directory (str, optional): Absolute path to the project directory.
                                          If provided, dataset paths within this directory will use relative paths.
                                          If None or datasets are outside, absolute paths will be used.
                                          Defaults to None.
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable.
                                        Defaults to 'markdown'.

    Returns:
        str: Generated R code for loading datasets

        Markdown format includes:
        - Complete R code in code block
        - Usage instructions
        - List of datasets included

        JSON format includes:
        - code: The generated R code
        - datasets: List of dataset names
        - file_path: Recommended file path (data.R)
        - instructions: Step-by-step usage instructions

    Generated Code Structure:
        1. Library import (library(teal))
        2. Dataset loading (readRDS() for .Rds, read.csv() for .csv)
        3. teal_data() object creation with all datasets
        4. Join keys configuration:
           - For standard ADaM datasets: Uses default_cdisc_join_keys
           - For non-standard datasets: Includes warning comments

    Workflow Integration:
        1. Use tealflow_discover_datasets to find datasets
        2. Pass the datasets_found array to this tool
        3. Save the generated code as data.R in the project root
        4. The app template will source this file

    Examples:
        - Generate loading code: datasets=[...from discovery...]
        - Get JSON format: datasets=[...], response_format="json"

    Note:
        - Datasets are sorted alphabetically for consistent output
        - Paths must be absolute (from discovery tool)
        - Currently supports Rds and csv formats
        - Extensible design for future format support
    """
    params = GenerateDataLoadingInput(
        datasets=datasets,
        project_directory=project_directory,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_generate_data_loading(params)


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

    This tool returns the base R code template that should be used to start any Teal app.
    The template includes data loading, configuration variables, and the basic structure
    for adding Teal modules.

    Args:
        response_format (str, optional): Output format - 'markdown' for human-readable or 'json' for machine-readable. Defaults to 'markdown'.

    Returns:
        str: Complete R code for the Teal app template

        The template includes:
        - Library imports (teal.modules.general, teal.modules.clinical)
        - Data source loading (knowledge_base/data.R)
        - Dataset configuration (ADSL, ADTTE, ADRS, ADQS, ADAE)
        - Configuration variables (arm_vars, strata_vars, facet_vars, etc.)
        - Helper variables (cs_arm_var, cs_strata_var, etc.)
        - App initialization with basic modules (tm_front_page, tm_data_table, tm_variable_browser)

    Usage:
        1. Get the template using this tool
        2. Use tealflow_search_modules_by_analysis to find modules for your analysis
        3. Use tealflow_generate_module_code to generate code for each module
        4. Add generated modules to the modules() section (line 78)
        5. Run the app

    Examples:
        - Get template in markdown: response_format="markdown"
        - Get template as JSON: response_format="json"

    Note:
        The template uses Flow's standard ADaM datasets (ADSL, ADTTE, ADRS, ADQS, ADAE).
        Modify the data source if using different datasets.
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
    parameters: dict | None = None,
    include_comments: bool = True
) -> str:
    """
    Generate R code for adding a module to a Teal application.

    This tool generates ready-to-use R code for adding a Teal module to your app.
    It includes all required parameters with sensible defaults based on the module's
    specifications and Flow's available datasets.

    Args:
        module_name (str, required): Name of the module to generate code for (e.g., 'tm_g_km', 'tm_t_coxreg', 'tm_g_scatterplot').
        parameters (dict[str, Any], optional): Optional parameter overrides as JSON object. Defaults to None. (Not yet implemented)
        include_comments (bool, optional): Whether to include explanatory comments in the generated code. Defaults to True.

    Returns:
        str: Complete R code snippet ready to paste into a Teal app

        Includes:
        - Module function call with proper syntax
        - All required parameters
        - Common optional parameters with defaults
        - Explanatory comments (if requested)
        - Usage instructions

    Examples:
        - Generate KM plot code: module_name="tm_g_km"
        - Generate Cox regression code: module_name="tm_t_coxreg"
        - Generate without comments: module_name="tm_g_km", include_comments=False

    Note:
        Generated code uses Flow's standard dataset configuration.
        You may need to adjust parameters for your specific use case.
    """
    params = GenerateModuleCodeInput(
        module_name=module_name,
        parameters=parameters,
        include_comments=include_comments
    )
    return await tealflow_generate_module_code(params)


@mcp.tool(
    name="tealflow_check_shiny_startup",
    annotations={
        "title": "Check Shiny App Startup",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def check_shiny_startup_tool(
    app_path: str = ".",
    app_filename: str = "app.R",
    timeout_seconds: int = 15
) -> str:
    """
    Check if a Shiny app starts without errors.

    This tool runs the Shiny app file using shiny::runApp() to detect startup errors
    without keeping the app running or waiting for user interaction. It's useful for
    validating that a Teal application has been correctly configured before attempting
    to run it interactively.

    Args:
        app_path (str, optional): Path to the Shiny app directory. Defaults to ".".
        app_filename (str, optional): Name of the app file to run (e.g., 'app.R', 'server.R'). Defaults to "app.R".
        timeout_seconds (int, optional): Maximum time in seconds to allow the app to start (1-120). Defaults to 15.

    Returns:
        str: JSON object with startup validation results

        Success response:
            {
                "status": "ok",
                "error_type": null,
                "message": "App started successfully",
                "logs_excerpt": "... last 20 lines of output ..."
            }

        Error response:
            {
                "status": "error",
                "error_type": "missing_package" | "syntax_error" | "object_not_found" |
                              "timeout" | "file_not_found" | "rscript_not_found" |
                              "connection_error" | "execution_error",
                "message": "Detailed error description",
                "logs_excerpt": "... last 30 lines of output ..."
            }

    Error Types:
        - missing_package: Required R package is not installed
        - syntax_error: R syntax error in app.R
        - object_not_found: Referenced R object does not exist
        - timeout: App did not start within the specified timeout
        - file_not_found: app.R file not found at specified path
        - rscript_not_found: Rscript command not available (R not installed)
        - connection_error: Network or file connection error
        - execution_error: Other R execution error

    Examples:
        - Check app in current directory: (no parameters needed)
        - Check app in specific directory: app_path="/path/to/app"
        - Check specific app file: app_filename="server.R"
        - Use longer timeout: timeout_seconds=30

    Note:
        This tool does not launch an interactive Shiny session. It only validates
        that the app can start without immediate errors. The process is terminated
        once startup is confirmed or an error is detected.
    """
    params = CheckShinyStartupInput(
        app_path=app_path,
        app_filename=app_filename,
        timeout_seconds=timeout_seconds
    )
    return await tealflow_check_shiny_startup(params)


@mcp.tool(
    name="tealflow_setup_renv_environment",
    annotations={
        "title": "Setup Renv Environment",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def setup_renv_environment_tool(
    project_path: str = ".",
    response_format: str = "json"
) -> str:
    """
    Prepare an R project directory so it is ready to run Teal Shiny applications.

    This tool initializes an renv environment and installs required packages
    (shiny, teal, teal.modules.general, teal.modules.clinical).

    **Behavior:**
    - If `renv.lock` exists: Restores packages at locked versions, then installs
      only packages missing from the lockfile. User's pinned versions are respected.
    - If no `renv.lock`: Initializes a new renv environment and installs all packages.

    **Steps performed:**
    1. Validates project path and R installation
    2. Installs renv package if missing
    3. Initializes renv (or restores existing lockfile)
    4. Installs required packages (only missing ones if lockfile exists)

    Args:
        project_path (str, optional): **ABSOLUTE** path to the R project directory.
            MUST be an absolute path (e.g., "/home/user/project" or "C:\\Users\\user\\project").
            Relative paths like "." will resolve to the MCP server's directory, not the user's project.
            Defaults to "." but should always be explicitly provided as an absolute path.
        response_format (str, optional): Output format - 'json' or 'markdown'. Defaults to 'json'.

    Returns:
        str: JSON/markdown with status, steps_completed, message, and logs_excerpt.

    Error Types:
        - filesystem_error: Project path does not exist
        - rscript_not_found: R is not installed or not in PATH
        - renv_install_failed: Failed to install or initialize renv
        - package_install_failed: Failed to install required packages

    Examples:
        - Setup current directory: (no parameters needed)
        - Setup specific project: project_path="/path/to/project"
    """
    params = SetupRenvEnvironmentInput(
        project_path=project_path,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_setup_renv_environment(params)


@mcp.tool(
    name="tealflow_snapshot_renv_environment",
    annotations={
        "title": "Snapshot Renv Environment",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def snapshot_renv_environment_tool(
    project_path: str = ".",
    response_format: str = "json"
) -> str:
    """
    Create an renv snapshot of the current R project environment.

    This tool captures the current state of installed R packages and records them
    in renv.lock. This creates a reproducible record of your project's dependencies
    that can be restored later or shared with others.

    **When to use this tool:**
    - After installing new packages
    - After updating existing packages
    - Before sharing your project with others
    - To create a reproducible checkpoint of your environment

    **Requirements:**
    - renv must already be initialized (use tealflow_setup_renv_environment first)
    - Project must have an active renv environment

    Args:
        project_path (str, optional): **ABSOLUTE** path to the R project directory.
            MUST be an absolute path (e.g., "/home/user/project" or "C:\\Users\\user\\project").
            Relative paths like "." will resolve to the MCP server's directory, not the user's project.
            Defaults to "." but should always be explicitly provided as an absolute path.
        response_format (str, optional): Output format - 'json' or 'markdown'. Defaults to 'json'.

    Returns:
        str: JSON/markdown with status, message, and logs_excerpt.

    Error Types:
        - filesystem_error: Project path does not exist
        - rscript_not_found: R is not installed or not in PATH
        - renv_not_initialized: renv has not been initialized in this project
        - snapshot_failed: Failed to create renv snapshot
        - execution_error: Unexpected error during snapshot

    Examples:
        - Snapshot current directory: (no parameters needed)
        - Snapshot specific project: project_path="/path/to/project"
        - Get markdown output: response_format="markdown"

    Note:
        This tool only snapshots packages that are used in your project code.
        Make sure you have library() calls in global.R or your R scripts for
        packages you want to include in the snapshot.
    """
    params = SnapshotRenvEnvironmentInput(
        project_path=project_path,
        response_format=ResponseFormat(response_format)
    )
    return await tealflow_snapshot_renv_environment(params)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
