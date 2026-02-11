# TealFlowMCP Tools Reference

Complete reference for all available TealFlowMCP tools.

## Quick Reference

- [Agent Guidance](#1-tealflow_agent_guidance) - **START HERE** - Get comprehensive guidance for Teal development
- [List Modules](#2-tealflow_list_modules) - List all available Teal modules
- [Search Modules](#3-tealflow_search_modules_by_analysis) - Search modules by analysis type
- [Get Module Details](#4-tealflow_get_module_details) - Get detailed module information
- [Generate Module Code](#5-tealflow_generate_module_code) - Generate R code for modules
- [Get App Template](#6-tealflow_get_app_template) - Get Teal application template
- [Generate Data Loading](#7-tealflow_generate_data_loading) - Generate R script for loading datasets
- [List Datasets](#8-tealflow_list_datasets) - List available clinical trial datasets
- [Discover Datasets](#9-tealflow_discover_datasets) - Scan directories for ADaM datasets
- [Check Dataset Requirements](#10-tealflow_check_dataset_requirements) - Check dataset compatibility
- [Get Dataset Info](#11-tealflow_get_dataset_info) - Get information about ADaM datasets
- [Setup R Environment](#12-tealflow_setup_renv_environment) - Initialize R project with renv
- [Snapshot R Environment](#13-tealflow_snapshot_renv_environment) - Snapshot current R environment state
- [Check Shiny Startup](#14-tealflow_check_shiny_startup) - Validate app startup

---

## 1. `tealflow_agent_guidance`

**START HERE** - Get comprehensive guidance for assisting users with Teal application development.

This is the primary tool that provides LLMs with essential context on how to use all other TealFlowMCP tools effectively. It returns the complete agent guidance document that explains workflows, best practices, and tool usage patterns.

---

## 2. `tealflow_list_modules`

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

---

## 3. `tealflow_search_modules_by_analysis`

Search for modules that perform a specific type of analysis.

**Parameters:**
- `analysis_type` (required): Type of analysis (e.g., "survival")
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "analysis_type": "survival analysis",
  "response_format": "markdown"
}
```

---

## 4. `tealflow_get_module_details`

Check if required datasets are available for a module.

**Parameters:**
- `module_name` (required): Module to check
- `available_datasets` (required): List of available datasets
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "module_name": "tm_g_km",
  "available_datasets": ["ADSL", "ADTTE"]
}
```

---

## 5. `tealflow_generate_module_code`

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

---

## 6. `tealflow_get_app_template`

Get the Teal application template as a starting point for building apps. The template includes data loading, and the basic structure for adding Teal modules.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

---

## 7. `tealflow_generate_data_loading`

Generate R script for loading ADaM datasets into a Teal application.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

---

## 8. `tealflow_list_datasets`

List available clinical trial datasets.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

---

## 9. `tealflow_discover_datasets`

Scan a directory for ADaM dataset files (.Rds, .csv) and extract dataset information.

**Parameters:**
- `directory_path` (required): Absolute path to directory containing datasets
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "directory_path": "/absolute/path/to/data",
  "response_format": "markdown"
}
```

---

## 10. `tealflow_check_dataset_requirements`

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

---

## 11. `tealflow_get_dataset_info`

Get detailed information about ADaM datasets, including their structure, required variables, and relationships.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

---

## 12. `tealflow_setup_renv_environment`

Initialize an R project environment with renv and install required packages for Teal apps.

**Parameters:**
- `project_path` (optional): Path to the project directory (default: ".")
- `response_format` (optional): "markdown" or "json" (default: "json")

**Example:**
```json
{
  "project_path": ".",
  "response_format": "json"
}
```

---

## 13. `tealflow_snapshot_renv_environment`

Snapshot the current R environment state using renv, creating or updating the renv.lock file.

**Parameters:**
- `project_path` (optional): Path to the project directory (default: ".")
- `response_format` (optional): "markdown" or "json" (default: "json")

**Example:**
```json
{
  "project_path": ".",
  "response_format": "json"
}
```

---

## 14. `tealflow_check_shiny_startup`
