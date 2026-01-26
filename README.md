# TealFlowMCP

An MCP (Model Context Protocol) server that enables LLMs to discover, understand, and generate Teal R Shiny applications for clinical trial data analysis.

## Prerequisites

* Python 3.10+

* uv (Python project manager) installed and available in your PATH.

## MCP Compatibility

This server implements the **Model Context Protocol (MCP)** standard and works with any MCP-compatible LLM client, including:

- **Claude Desktop** (Anthropic)
- **Claude Code** (VS Code extension)
- **Other MCP-compatible tools** that support the MCP stdio protocol

The server is LLM-agnostic - it provides tools that any LLM can use to build Teal applications.

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
├── workspace/                 # Metadata and dataset files
├── tests/                     # Automated tests
├── pyproject.toml             # Project metadata & dependencies
├── uv.lock                    # Lockfile for exact versions
└── README.md
```

The refactored structure provides:
- **Separation of concerns** - Each module has a clear responsibility
- **Easy testing** - Utilities and data loaders can be tested independently
- **Maintainability** - Changes are localized to specific modules
- **Extensibility** - New tools can be added without modifying existing code

## Overview

The Teal Flow MCP server provides tools to work with the Teal framework programmatically. It helps with:

- **Discovering** available Teal modules (clinical and general)
- **Understanding** module requirements and parameters
- **Checking** dataset compatibility
- **Searching** for modules by analysis type
- **Generating** R code for Teal applications

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

## Available Tools

### 1. `tealflow_list_modules`

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

### 2. `tealflow_get_module_details`

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

### 3. `tealflow_search_modules_by_analysis`

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

### 4. `tealflow_check_dataset_requirements`

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

### 5. `tealflow_list_datasets`

List available clinical trial datasets.

**Parameters:**
- `response_format` (optional): "markdown" or "json" (default: "markdown")

**Example:**
```json
{
  "response_format": "markdown"
}
```

### 6. `tealflow_generate_module_code`

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

### Example: Claude Desktop Configuration

Below is an example using Claude Desktop. For other MCP clients, consult their documentation on adding custom MCP servers.

Add the following to your Claude Desktop configuration file:

**Configuration File Locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration Example (macOS/Linux):**
```json
{
  "mcpServers": {
    "tealflow": {
      "command": "python",
      "args": ["/path/to/TealFlowMCP/tealflow_mcp.py"]
    }
  }
}
```

**Configuration Example (Windows):**
```json
{
  "mcpServers": {
    "tealflow": {
      "command": "python",
      "args": ["C:\\path\\to\\TealFlowMCP\\tealflow_mcp.py"]
    }
  }
}
```

### Configuring Other MCP Clients

For other MCP-compatible clients, the server should be configured to run:
```bash
python /path/to/TealFlowMCP/tealflow_mcp.py
```

The server communicates via stdio using the standard MCP protocol, making it compatible with any MCP client that supports stdio-based servers.

**Key configuration details for any MCP client:**
- **Command**: `python` (or `python3`)
- **Arguments**: `["/absolute/path/to/TealFlowMCP/tealflow_mcp.py"]`
- **Protocol**: stdio (standard MCP)
- **Python Version**: 3.10 or higher required

## Getting Started

Once configured with your MCP-compatible LLM client, you can request help building Teal apps using natural language. Here are common patterns:

### Build a Complete App

**User Request:**
> I have ADSL and ADTTE datasets. Build me a Teal app with Kaplan-Meier plots and Cox regression.

**The LLM will:**
- Search for survival analysis modules using `tealflow_search_modules_by_analysis`
- Validate dataset compatibility using `tealflow_check_dataset_requirements`
- Generate complete app code with both modules using `tealflow_generate_module_code`
- Explain any parameters that need configuration

### Explore Available Modules

**User Request:**
> What modules can I use for adverse event analysis?

**The LLM will:**
- Search for adverse event modules using `tealflow_search_modules_by_analysis`
- List compatible options with descriptions
- Suggest which datasets are needed

### Get Module Details

**User Request:**
> Show me the parameters for tm_g_km

**The LLM will:**
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

## Data Sources

The MCP server reads from workspace files in the Flow project root:
- `workspace/teal_modules_clinical_dataset_requirements.json`
- `workspace/teal_modules_clinical_modules_requirements.json`
- `workspace/teal_modules_general_modules_requirements.json`
- `workspace/teal.md`

The server is located at `./tealflow_mcp.py` and references `./workspace/` for data files.

## Architecture

### Design Principles

1. **Workflow-Oriented**: Tools enable complete workflows, not just data dumps
2. **Context-Efficient**: Optimized responses for LLM context windows
3. **Human-Readable**: Clear, actionable information with examples
4. **Error-Guided**: Helpful error messages that guide toward solutions

### Response Formats

All tools support two output formats:

- **Markdown** (default): Human-readable with formatting, headers, and structure
- **JSON**: Machine-readable structured data for programmatic processing

### Error Handling

- Input validation via Pydantic models
- Fuzzy matching for module name typos
- Clear error messages with suggestions
- Guidance on next steps

## Development

### Project Structure

```
mcp/
├── server/
│   ├── tealflow_mcp.py              # Main MCP server implementation
│   └── tealflow_mcp_requirements.txt # Python dependencies
├── docs/
│   └── README.md                     # This documentation
└── tests/
    └── test_mcp_server.py           # Unit tests

workspace/                            # Data files (at project root)
```

### Adding New Tools

To add a new tool:

1. Define a Pydantic input model
2. Implement the tool function with `@mcp.tool()` decorator
3. Add comprehensive docstring
4. Include proper error handling
5. Support both markdown and JSON output formats

### Code Quality Checklist

- [ ] All parameters use Pydantic validation
- [ ] Comprehensive docstrings with examples
- [ ] Error handling with helpful messages
- [ ] Both markdown and JSON output formats
- [ ] Type hints throughout
- [ ] Character limit enforcement (25,000 chars)
- [ ] Async/await for I/O operations

## Testing

### Manual Testing

```bash
# Start the server
python mcp/server/tealflow_mcp.py

# The server will run in stdio mode and wait for MCP protocol messages
```

### Integration Testing

Test the server with any MCP-compatible client:

1. Configure the server in your MCP client
2. Ask your LLM to use the tealflow tools
3. Verify responses are correct and helpful

### Example Test Queries

```
"List all clinical modules for survival analysis"
"What parameters does tm_g_km require?"
"Generate code for a Kaplan-Meier plot"
"Check if I can use tm_t_coxreg with my datasets"
```

## Limitations

- Code generation currently only supports clinical modules (37 modules)
- General modules (16 modules) can be discovered and documented, but code generation is not yet implemented
- Some complex modules (e.g., patient profile with data_extract_spec) may need manual parameter adjustment
- Requires workspace JSON files to be present
- No caching of generated code

## Future Enhancements

- [ ] Full parameter customization in code generation
- [ ] Support for general modules in code generation
- [ ] Code validation and syntax checking
- [ ] Template-based code generation with variants
- [ ] Integration with Flow's app generation system
- [ ] Caching and performance optimizations
- [ ] Extended search with NLP/embeddings

## Frequently Asked Questions (FAQ)

### Does the Tealflow MCP need an API key or internet connection?

**No!** The Tealflow MCP server is a **local data provider** that only reads JSON files from the workspace directory. It provides tools to LLMs but doesn't make API calls itself.

You still need an API key for your LLM client (e.g., Anthropic API for Claude, OpenAI API for GPT, etc.) to work, but the MCP server itself doesn't use or need any API keys or internet connection.

### How can multiple people on my team use this MCP?

Each team member needs to set up their own instance:

1. **Get the Flow project:**
   ```bash
   git clone <your-flow-repo-url>
   cd flow
   ```

2. **Install dependencies:**
   ```bash
   pip install -r tealflow_mcp_requirements.txt
   ```

3. **Configure your MCP client:**
   - Locate your MCP client's config file (see Configuration section above)
   - Add the tealflow MCP server configuration with **your local path**
   - Example: `"args": ["/Users/YOUR_USERNAME/projects/flow/mcp/server/tealflow_mcp.py"]`

4. **Restart your MCP client**

The MCP runs locally on each person's machine - no shared server needed. Each person maintains their own copy of the Flow project.

**Team Sharing Options:**
- **Individual copies** (recommended): Everyone clones the repo and maintains their own copy
- **Shared network directory**: Put Flow on a shared drive and everyone points to the same location
- **Custom distribution**: Package the MCP with data files and distribute as a standalone tool

### Can I use this MCP in a different project?

Yes, but the MCP requires the Flow project's workspace data files to function. You have two options:

**Option A: Reference the Flow project** (recommended)
- Keep the Flow project in a central location
- Configure your MCP client to point to that location
- No need to copy files

**Option B: Copy to your project**
1. Copy the MCP files to your project:
   ```bash
   cp -r mcp /path/to/your/project/
   cp -r workspace /path/to/your/project/
   ```

2. Update your MCP client config to point to the new location

3. Install dependencies in your project

**Note:** The workspace directory contains all the Teal module metadata (37 clinical + 16 general modules). Without these JSON files, the MCP won't work.

### What platforms are supported?

The MCP works on **macOS, Windows, and Linux** as long as you have Python 3.10+ installed.

Configuration file locations vary by platform:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

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

### Can I use this with Claude Code (VS Code extension)?

Yes! If you're using this Flow project as your workspace in VS Code with Claude Code, the MCP server is already configured in `.claude/settings.local.json` with pre-approved permissions for all tealflow tools.

You don't need to add anything to Claude Desktop config - just use Claude Code in this workspace.

### What if I get "Required data file not found" errors?

This means the MCP can't find the workspace JSON files. Ensure:

1. The workspace directory exists at project root (`../../workspace/` relative to the MCP server)
2. All required files are present:
   - `teal_modules_clinical_dataset_requirements.json`
   - `teal_modules_clinical_modules_requirements.json`
   - `teal_modules_general_modules_requirements.json`
3. The files are readable (check permissions)

The MCP looks for these files in `Path(__file__).parent.parent.parent / "workspace"` (see mcp/server/tealflow_mcp.py:31).

### Is there a limit to how many times I can use the MCP tools?

No! The MCP is a local service that reads static JSON files. There are no API rate limits, usage quotas, or costs associated with using the MCP tools themselves.

However, using your LLM client (e.g., Claude Desktop, GPT-based tools, etc.) still consumes your API usage/subscription according to your provider's pricing.

## Troubleshooting

### "Module not found" error

Make sure you're using the correct module name. Use `tealflow_list_modules` to see all available modules, or the search tool will suggest corrections for typos.

### "Required data file not found"

Ensure the workspace directory exists and contains the required JSON files:
- `teal_modules_clinical_dataset_requirements.json`
- `teal_modules_clinical_modules_requirements.json`
- `teal_modules_general_modules_requirements.json`

### Server won't start

Check that dependencies are installed:
```bash
pip install -r tealflow_mcp_requirements.txt
```

## Support

For issues or questions:
- Check the workspace directory contains all required JSON files
- Verify Python version is 3.10+
- Ensure all dependencies are installed
- Review error messages for specific guidance

## License

This MCP server is part of the Flow project by Appsilon.
