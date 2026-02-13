# TealFlowMCP

[![PyPI version](https://badge.fury.io/py/tealflow-mcp.svg)](https://badge.fury.io/py/tealflow-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/tealflow-mcp.svg)](https://pypi.org/project/tealflow-mcp/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Downloads](https://pepy.tech/badge/tealflow-mcp)](https://pepy.tech/project/tealflow-mcp)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://appsilon.github.io/TealFlowMCP/)

An MCP (Model Context Protocol) server that enables LLMs to discover, understand, and generate [Teal](https://insightsengineering.github.io/teal/) R Shiny applications for clinical trial data analysis.

Currently supports two Teal module packages:
- [teal.modules.general](https://insightsengineering.github.io/teal.modules.general/) - General-purpose analysis modules
- [teal.modules.clinical](https://insightsengineering.github.io/teal.modules.clinical/) - Clinical trial-specific modules

## Documentation

- **[Quickstart Guide](https://appsilon.github.io/TealFlowMCP/QUICKSTART/)** - Get started with VSCode and GitHub Copilot
- **[Tool Reference](https://appsilon.github.io/TealFlowMCP/TOOLS/)** - Complete reference for all 14 MCP tools
- **[Configuration Guide](https://appsilon.github.io/TealFlowMCP/CONFIGURATION/)** - Setup, usage examples, and FAQs

## Quick Start

**New to TealFlowMCP?** Check out the [Quickstart Guide](https://appsilon.github.io/TealFlowMCP/QUICKSTART/) for step-by-step instructions to get up and running with VSCode and GitHub Copilot.

## Prerequisites

* Python 3.10+
* R (required for running generated Teal applications)

**For development/source installation only:**
* uv (Python project manager) - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)

## MCP Compatibility

This server implements the **Model Context Protocol (MCP)** standard and works with any MCP-compatible LLM client, including:

- **Claude Code**
- **GitHub Copilot**
- **Cursor**
- **Other MCP-compatible tools** that support the MCP stdio protocol

The server is LLM-agnostic—it provides tools that any LLM can use to build Teal applications.

### Adding to Your Editor/IDE

**For PyPI installation:**

```json
{
  "tealflow-mcp": {
    "command": "tealflow-mcp"
  }
}
```

**For source installation:**

```json
{
  "tealflow-mcp": {
    "command": "uv",
    "args": ["--directory", "/absolute/path/to/TealFlowMCP", "run", "tealflow_mcp.py"]
  }
}
```

Replace `/absolute/path/to/TealFlowMCP` with the actual absolute path to your cloned repository.

Consult your editor's documentation for the exact location of the MCP configuration file. See the [Quickstart Guide](https://appsilon.github.io/TealFlowMCP/QUICKSTART/) and [Configuration Guide](https://appsilon.github.io/TealFlowMCP/CONFIGURATION/) for detailed setup instructions.

## Architecture

The MCP server is organized as a modular Python package for maintainability and extensibility:

```
TealFlowMCP/
├── tealflow_mcp.py            # Backward-compatibility wrapper
├── tealflow_mcp/              # Main package
│   ├── core/                  # Constants and enums
│   ├── data/                  # Data loaders
│   ├── knowledge_base/        # Metadata and templates
│   ├── models/                # Pydantic input models
│   ├── server.py              # MCP server implementation
│   ├── tools/                 # MCP tool implementations
│   └── utils/                 # Utilities and formatters
├── docs/                      # Documentation
├── tests/                     # Automated tests
├── sample_data/               # Sample ADaM datasets
├── .github/                   # CI/CD workflows
├── pyproject.toml             # Project metadata & dependencies
├── uv.lock                    # Lockfile for exact versions
└── README.md
```

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install tealflow-mcp
```

### Option 2: Install from Source (Development)

Clone the repository and install dependencies:

```bash
git clone https://github.com/Appsilon/TealFlowMCP.git
cd TealFlowMCP
uv sync
```

### Verify Installation

For pip installation, verify the package is installed:
```bash
python -c "import tealflow_mcp; print(f'TealFlowMCP version {tealflow_mcp.__version__}')"
```

For source installation, run the test suite:
```bash
uv run python -m pytest tests/test_mcp_server.py -v
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

## Code Quality

### Check Linting

Check for linting issues:

```bash
uv run ruff check tealflow_mcp/ tests/
```

### Auto-fix Linting Issues

Automatically fix linting issues:

```bash
uv run ruff check tealflow_mcp/ tests/ --fix
```

### Format Code

Format code consistently:

```bash
uv run ruff format tealflow_mcp/ tests/
```

### Type Checking

Run static type checking:

```bash
uv run mypy tealflow_mcp/
```

### Run All Checks

Run all code quality checks at once (same as CI):

```bash
uv run ruff check tealflow_mcp/ tests/ && \
uv run ruff format tealflow_mcp/ tests/ --check && \
uv run mypy tealflow_mcp/ && \
uv run python -m pytest tests/ -v
```

## Continuous Integration

This project uses GitHub Actions for automated testing and code quality checks.

The CI pipeline runs on every push and pull request:
- ✅ Linting and formatting checks
- ✅ Type checking with mypy
- ✅ Tests on Python 3.10, 3.11, and 3.12
- ✅ Code coverage reporting

## Manual Testing

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

**For PyPI installation:**

```bash
tealflow-mcp
```

**For source installation:**

```bash
uv --directory /absolute/path/to/TealFlowMCP/ run tealflow_mcp.py
```

You can also test the MCP using the MCP inspector:

**PyPI installation:**
```bash
npx @modelcontextprotocol/inspector tealflow-mcp
```

**Source installation:**
```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/TealFlowMCP/ run tealflow_mcp.py
```

## Available Tools

TealFlowMCP provides 14 tools for building Teal applications:

**Agent Guidance:**
- `tealflow_agent_guidance` - **START HERE** - Get comprehensive development guidance and learn how to use all other tools

**Module Discovery & Search:**
- `tealflow_list_modules` - List all available Teal modules
- `tealflow_search_modules_by_analysis` - Find modules by analysis type
- `tealflow_get_module_details` - Get detailed module information

**Code Generation:**
- `tealflow_generate_module_code` - Generate R code for modules
- `tealflow_get_app_template` - Get base Teal app template
- `tealflow_generate_data_loading` - Generate R script for loading datasets

**Dataset Management:**
- `tealflow_list_datasets` - List available clinical trial datasets
- `tealflow_discover_datasets` - Scan directories for ADaM datasets
- `tealflow_check_dataset_requirements` - Check dataset compatibility
- `tealflow_get_dataset_info` - Get information about ADaM datasets

**Environment & Validation:**
- `tealflow_setup_renv_environment` - Initialize R environment with renv
- `tealflow_snapshot_renv_environment` - Snapshot current R environment state
- `tealflow_check_shiny_startup` - Validate app startup

**[View complete tool reference →](https://appsilon.github.io/TealFlowMCP/TOOLS/)**

## Configuration

TealFlowMCP works with any MCP-compatible client (Claude Desktop, Claude Code, GitHub Copilot, Cursor, etc.).

**Basic Configuration:**
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

**[View complete configuration guide →](https://appsilon.github.io/TealFlowMCP/CONFIGURATION/)**

## Quick Start

Once configured, you can use natural language to build Teal apps:

**Example:**
> I have ADSL and ADTTE datasets. Build me a Teal app with Kaplan-Meier plots and Cox regression.

The LLM will automatically:
- Setup the R environment
- Search for relevant modules
- Validate dataset compatibility
- Generate complete app code

**[View usage examples and FAQs →](https://appsilon.github.io/TealFlowMCP/CONFIGURATION/)**

## About Appsilon

TealFlowMCP is developed by [Appsilon](https://appsilon.com), a trusted technology partner for pharmaceutical and life sciences companies specializing in accelerating drug development through open-source solutions. Appsilon helps organizations transition from legacy systems to modern, validated open-source analytics while maintaining strict regulatory compliance.

Learn more at [appsilon.com](https://appsilon.com)
