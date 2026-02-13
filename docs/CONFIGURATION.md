# Configuration Guide

This guide explains how to configure TealFlowMCP with various MCP-compatible clients.

## MCP Client Compatibility

TealFlowMCP works with any MCP-compatible client:
- **Claude Desktop**
- **Claude Code**
- **GitHub Copilot**
- **Cursor**
- **Other MCP-compatible tools** that support the MCP stdio protocol

## Installation

Before configuration, install TealFlowMCP:

**PyPI Installation (Recommended):**
```bash
pip install tealflow-mcp
# or
pipx install tealflow-mcp
```

**Source Installation (Development):**
```bash
git clone https://github.com/Appsilon/TealFlowMCP.git
cd TealFlowMCP
uv sync
```

## Basic Configuration

### PyPI Installation

If you installed from PyPI, use this simple configuration:

```json
{
  "servers": {
    "tealflow-mcp": {
      "command": "tealflow-mcp"
    }
  }
}
```

### Source Installation

If you're running from source, use this configuration:

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

**Important:** Replace `/absolute/path/to/TealFlowMCP` with the actual absolute path to your cloned repository.

### Finding Configuration Files

Different MCP clients store configuration in different locations:

- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- **GitHub Copilot**: Configured through VS Code settings
- **Cursor**: Check Cursor's MCP settings documentation

## Getting Started Workflow

Once configured, simply start a conversation with your LLM and describe what you want to build:

**You just need to:**
- Describe the Teal app you want to create using natural language

**The MCP will automatically:**
- Setup the R environment (install required packages with renv)
- Discover datasets in your project directory
- Find compatible modules
- Generate the complete app code

**Example:**
> "I have ADSL and ADTTE datasets in my data/ folder. Build me a Teal app with Kaplan-Meier plots and Cox regression."

The LLM will handle everything - from environment setup to code generation!

## Usage Patterns

### Build a Complete App

**User Request:**
> I have ADSL and ADTTE datasets. Build me a Teal app with Kaplan-Meier plots and Cox regression.

**The LLM will automatically:**
- Setup the R environment and install required packages
- Discover your ADSL and ADTTE datasets
- Search for survival analysis modules (Kaplan-Meier, Cox regression)
- Validate dataset compatibility
- Generate complete app code with both modules
- Provide the ready-to-run Teal application

### Explore Available Modules

**User Request:**
> What modules can I use for adverse event analysis?

**The LLM will automatically:**
- Search for adverse event analysis modules
- List compatible options with descriptions
- Explain which datasets are needed (e.g., ADSL, ADAE)
- Provide recommendations based on your analysis goals

### Get Module Details

**User Request:**
> Show me the parameters for tm_g_km

**The LLM will automatically:**
- Fetch detailed parameter information for tm_g_km
- Explain required vs optional parameters
- Show parameter types and defaults
- Help you understand how to customize the module

## Tips for Best Results

- **Be specific about datasets**: Mention which ADaM datasets you have (ADSL, ADTTE, ADAE, etc.)
- **Describe the analysis**: Use terms like "survival", "adverse events", "forest plot" rather than module names
- **Ask for explanations**: Your LLM can explain generated code and suggest configurations

## Technical Examples

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

## Frequently Asked Questions

### Does TealFlowMCP need an API key or internet connection?

**No!** TealFlowMCP is a **local data provider** that only reads JSON files. It provides tools to LLMs but doesn't make API calls itself.

You still need an API key for your LLM client (e.g., Anthropic API for Claude, OpenAI API for GPT, etc.), but the MCP server itself doesn't use or need any API keys or internet connection.

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
- Dependencies are installed (`uv sync`)
- MCP client was fully restarted

### Is there a limit to how many times I can use the MCP tools?

No! The MCP is a local service that reads static JSON files. There are no API rate limits, usage quotas, or costs associated with using the MCP tools themselves.

However, using your LLM client (e.g., Claude Desktop, GPT-based tools, etc.) still consumes your API usage/subscription according to your provider's pricing.
