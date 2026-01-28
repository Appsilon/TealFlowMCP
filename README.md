# TealFlowMCP

An MCP (Model Context Protocol) server that enables LLMs to discover, understand, and generate Teal R Shiny applications for clinical trial data analysis.

## Quick Start

**New to TealFlowMCP?** Check out the [Quickstart Guide](QUICKSTART.md) for step-by-step instructions to get up and running with VSCode and GitHub Copilot.

## Prerequisites

* Python 3.10+

* uv (Python project manager) installed and available in your PATH.

## MCP Compatibility

This server implements the **Model Context Protocol (MCP)** standard and works with any MCP-compatible LLM client, including:

- **Claude Code**
- **GitHub Copilot**
- **Cursor**
- **Other MCP-compatible tools** that support the MCP stdio protocol

The server is LLM-agnostic—it provides tools that any LLM can use to build Teal applications.

## Architecture

The MCP server is organized as a modular Python package for maintainability and extensibility:

```
TealFlowMCP/
├── tealflow_mcp.py            # MCP server entrypoint
├── tealflow_mcp/              # Source package
│   ├── core/
│   ├── data/
│   ├── models/
│   ├── tools/
│   └── utils/
├── knowledge_base/            # Metadata and dataset files
├── tests/                     # Automated tests
├── pyproject.toml             # Project metadata & dependencies
├── uv.lock                    # Lockfile for exact versions
└── README.md
```

## Installation

### Install Dependencies

Install dependencies with uv:

```
uv sync
```

### Verify Installation

```bash
uv run python tests/test_mcp_server.py
```

## Testing

### Run All Tests

Run the complete test suite:

```bash
uv run python -m pytest tests/ -v
```

### Run Specific Test Files

```bash
# Test MCP server functionality
uv run python -m pytest tests/test_mcp_server.py -v

# Test dataset discovery
uv run python -m pytest tests/test_discovery.py -v

# Test ADaM name extraction
uv run python -m pytest tests/test_extract_adam_name.py -v
```

### Run Single Test

```bash
uv run python -m pytest tests/test_discovery.py::TestDatasetDiscovery::test_discover_rds_files -v
```

### Run with Coverage

```bash
uv run python -m pytest tests/ --cov=tealflow_mcp --cov-report=term-missing -v
```

### Manual Testing

For quick manual verification:

```bash
# Test MCP server manually
uv run python tests/test_mcp_server.py

# Test discovery tool with sample data
uv run python -c "
from tealflow_mcp.tools.discovery import discover_datasets
import os
result = discover_datasets(os.path.abspath('sample_data'))
print(f'Found {result[\"count\"]} datasets')
"
```

## Running the MCP

The MCP can be run with a command:

```bash
uv --directory /absolute/path/to/TealFlowMCP/ run tealflow_mcp.pyuv run python tealflow_mcp.py
```

You can also test the MCP using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/TealFlowMCP/ run tealflow_mcp.py
```

## Available Tools

### 1. `tealflow_agent_guidance`

Get comprehensive guidance for assisting users with Teal application development.

### 2. `tealflow_list_modules`

List all available Teal modules with descriptions and dataset requirements.

**Parameters:**
- `package` (optional): Filter by "clinical", "general", or "all" (default: "all")
- `category` (optional): Filter by category (e.g., "graphics", "tables")
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "package": "clinical",
  "response_format": "markdown"
}
```

### 3. `tealflow_get_module_details`

Get comprehensive details about a specific module including all parameters.

**Parameters:**
- `module_name` (required): Name of the module (e.g., "tm_g_km")
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "module_name": "tm_g_km",
  "response_format": "markdown"
}
```

### 4. `tealflow_search_modules_by_analysis`

Search for modules that perform a specific type of analysis.

**Parameters:**
- `analysis_type` (required): Type of analysis (e.g., "survival", "kaplan-meier")
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "analysis_type": "survival analysis",
  "response_format": "markdown"
}
```

### 5. `tealflow_check_dataset_requirements`

Check if required datasets are available for a module.

**Parameters:**
- `module_name` (required): Module to check
- `available_datasets` (optional): List of available datasets (defaults to Flow's standard)
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "module_name": "tm_g_km",
  "available_datasets": ["ADSL", "ADTTE"]
}
```

### 6. `tealflow_list_datasets`

List available clinical trial datasets.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

### 7. `tealflow_get_app_template`

Get the Teal application template as a starting point for building apps. The template includes data loading, configuration variables (arm_vars, strata_vars, etc.), and the basic structure for adding Teal modules.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

### 8. `tealflow_generate_module_code`

Generate R code for adding a module to a Teal app.

**Parameters:**
- `module_name` (required): Module to generate code for
- `parameters` (optional): Parameter overrides (not yet fully implemented)
- `include_comments` (optional): Include comments (default: true)

**Example:**
```json
{
  "module_name": "tm_g_km",
  "include_comments": true
}
```

### 7. `tealflow_check_shiny_startup`

Validate that a Shiny app starts without errors. Runs the app file using `shiny::runApp()` with a timeout to detect startup issues without blocking indefinitely.

**Parameters:**
- `app_path` (optional): Path to the Shiny app directory (default: ".")
- `app_filename` (optional): Name of the app file to run, e.g., "app.R", "server.R" (default: "app.R")
- `timeout_seconds` (optional): Maximum time in seconds to allow the app to start, range 1-120 (default: 15)

**Example:**
```json
{
  "app_path": ".",
  "app_filename": "app.R",
  "timeout_seconds": 15
}
```

**Response Format:**
Returns a JSON object with:
- `status`: "ok" or "error"
- `error_type`: Classification of error (if any)
- `message`: Human-readable description
- `logs_excerpt`: Relevant output from the app startup

**Error Types:**
- `missing_package`: Required R package not installed
- `syntax_error`: R syntax error in app file
- `object_not_found`: Referenced object does not exist
- `timeout`: App did not start within timeout period
- `file_not_found`: App file not found at specified path
- `rscript_not_found`: R not installed or not in PATH
- `connection_error`: Network or file connection issue
- `execution_error`: Other R execution error

**Example Success Response:**
```json
{
  "status": "ok",
  "error_type": null,
  "message": "App started successfully",
  "logs_excerpt": "=== STDOUT ===\nListening on http://127.0.0.1:3838"
}
```

**Example Error Response:**
```json
{
  "status": "error",
  "error_type": "missing_package",
  "message": "Missing R package: teal.modules.clinical",
  "logs_excerpt": "=== STDERR ===\nError in library(teal.modules.clinical) : \n  there is no package called 'teal.modules.clinical'"
}
```

**Common Use Cases:**
- **After adding modules**: Validate the app starts correctly after code generation
- **Debugging startup issues**: Get structured error information to diagnose problems
- **CI/CD validation**: Automated testing of app startup in pipelines
- **Pre-deployment checks**: Ensure app is ready before sharing with users
- **Multiple app files**: Validate different Shiny app structures (app.R, server.R, ui.R)

**Best Practices:**
- Use appropriate timeouts (simple apps: 5-10s, complex apps: 20-30s)
- Check status after each module addition during development
- Focus on fixing startup errors only (missing packages, syntax issues)
- Don't retry indefinitely - report persistent errors after 2-3 attempts
- Specify `app_filename` when working with non-standard app structures

## Configuration for MCP Clients

This MCP server works with any MCP-compatible client (Claude Desktop, Claude Code, or other LLM tools that support the Model Context Protocol).

**Configuration Example:**
```json
{
	"servers": {
    "tealflow-mcp": {
	    "command": "uv",
			"args": [
        "--directory",
        "/absolute/path/to/TealFlowMCP",
        "run",
        "tealflow_mcp.py"
      ]
	  }
	}
}
```

## Getting Started

Once configured with your MCP-compatible LLM client, you can request help building Teal apps using natural language.

__NOTE:__ Current version requires manual environment setup:

1. Prepare your R environment - make sure that required R packages are installed. This includes `shiny`, `teal`, `teal.modules.general` and `teal.modules.clinical`. Using `renv` is strongly recommended.
2. Add a data directory to your project. Sample data can be found in the `./sample_data` directory.

Here are common patterns for prompts that can be used to build Teal applications:

### Build a Complete App

**User Request:**
> I have ADSL and ADTTE datasets. Build me a Teal app with Kaplan-Meier plots and Cox regression.

**The LLM will:**
- Run `tealflow_agent_guidance` to check the next steps.
- Get the app template using `tealflow_get_app_template` (when starting from scratch).
- Search for survival analysis modules using `tealflow_search_modules_by_analysis`
- Validate dataset compatibility using `tealflow_check_dataset_requirements`
- Generate complete app code with both modules using `tealflow_generate_module_code`
- Explain any parameters that need configuration

### Explore Available Modules

**User Request:**
> What modules can I use for adverse event analysis?

**The LLM will:**
- Run `tealflow_agent_guidance` to check the next steps.
- Search for adverse event modules using `tealflow_search_modules_by_analysis`
- List compatible options with descriptions
- Suggest which datasets are needed

### Get Module Details

**User Request:**
> Show me the parameters for tm_g_km

**The LLM will:**
- Run `tealflow_agent_guidance` to check the next steps.
- Fetch detailed parameter information using `tealflow_get_module_details`
- Explain required vs optional parameters
- Show parameter types and defaults

### Tips for Best Results

- **Be specific about datasets**: Mention which ADaM datasets you have (ADSL, ADTTE, ADAE, etc.)
- **Describe the analysis**: Use terms like "survival", "adverse events", "forest plot" rather than module names
- **Ask for explanations**: Your LLM can explain generated code and suggest configurations

## Usage Examples (Technical Reference)

### Example 1: Discover Kaplan-Meier modules

```
User: "I need to create a Kaplan-Meier survival plot for my clinical trial data"

The LLM uses these MCP tools:
1. tealflow_search_modules_by_analysis with analysis_type="kaplan-meier"
2. tealflow_get_module_details with module_name="tm_g_km"
3. tealflow_check_dataset_requirements with module_name="tm_g_km"
4. tealflow_generate_module_code with module_name="tm_g_km"
```

### Example 2: Find modules for specific datasets

```
User: "What analysis modules can I use with ADSL and ADTTE datasets?"

The LLM uses these MCP tools:
1. tealflow_list_datasets to understand available data
2. tealflow_list_modules with package="clinical"
3. Filters results to show modules requiring ADSL and ADTTE
```

### Example 3: Generate code for Cox regression

```
User: "Generate code for a Cox regression analysis module"

The LLM uses these MCP tools:
1. tealflow_search_modules_by_analysis with analysis_type="cox regression"
2. tealflow_get_module_details with module_name="tm_t_coxreg"
3. tealflow_generate_module_code with module_name="tm_t_coxreg"
```

## Frequently Asked Questions (FAQ)

### Does the Tealflow MCP need an API key or internet connection?

**No!** The Tealflow MCP server is a **local data provider** that only reads JSON files. It provides tools to LLMs but doesn't make API calls itself.

You still need an API key for your LLM client (e.g., Anthropic API for Claude, OpenAI API for GPT, etc.) to work, but the MCP server itself doesn't use or need any API keys or internet connection.

### How can multiple people on my team use this MCP?

Each team member needs to set up their own instance. The MCP runs locally on each person's machine - no shared server needed. Each person maintains their own copy of the MCP.

### How do I verify the MCP is working?

After configuring and restarting your MCP client:

1. Open a new conversation in your MCP client
2. Ask: *"List all clinical modules for survival analysis"*
3. The LLM should use the `tealflow_search_modules_by_analysis` tool
4. You should see results about tm_g_km, tm_t_coxreg, tm_t_tte, etc.

If you don't see the MCP tools being used, check:
- Configuration file syntax is valid JSON
- File path is correct and absolute (not relative)
- Python is in your PATH
- Dependencies are installed
- MCP client was fully restarted

### Is there a limit to how many times I can use the MCP tools?

No! The MCP is a local service that reads static JSON files. There are no API rate limits, usage quotas, or costs associated with using the MCP tools themselves.

However, using your LLM client (e.g., Claude Desktop, GPT-based tools, etc.) still consumes your API usage/subscription according to your provider's pricing.
