# TealFlowMCP Quickstart Guide

Get started with TealFlowMCP in VSCode in just a few minutes! This guide walks you through everything you need to build Teal R Shiny applications using AI assistance.

## What You'll Need

- **VSCode** with GitHub Copilot extension installed
- **Python 3.10 or higher**
- **R** installed with required packages (see [R Setup](#r-setup) below)

## Installation Options

Choose one of the following installation methods:

### Option A: Install from PyPI (Recommended)

This is the easiest way to get started.

#### Step 1: Install the Package

```bash
pip install tealflow-mcp
```

Or using pipx for isolated installation:

```bash
pipx install tealflow-mcp
```

#### Step 2: Verify Installation

```bash
python -c "import tealflow_mcp; print(f'TealFlowMCP version {tealflow_mcp.__version__}')"
```

#### Step 3: Configure VSCode

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS)
2. Type **"MCP: Add Server"** and select it
3. Choose **"Command"** as the server type
4. Enter the command: `tealflow-mcp`

Or manually add this configuration:

```json
"tealflow-mcp": {
  "command": "tealflow-mcp"
}
```

### Option B: Install from Source (Development)

Use this if you want to modify the code or contribute to development.

#### Step 1: Install uv

`uv` is a fast Python package manager that TealFlowMCP uses to manage dependencies.

Follow the official installation guide: **https://docs.astral.sh/uv/getting-started/installation/**

After installation, verify it's working:

```bash
uv --version
```

#### Step 2: Download the Repository

Clone the TealFlowMCP repository to your local machine:

```bash
git clone https://github.com/Appsilon/TealFlowMCP.git
cd TealFlowMCP
```

**Important:** Note the absolute path to this directory. You'll need it for the VSCode configuration. You can get the absolute path with:

```bash
pwd
```

#### Step 3: Install Dependencies

Install all Python dependencies using uv:

```bash
uv sync
```

This creates a virtual environment and installs all required packages based on the `pyproject.toml` file.

#### Step 4: Configure VSCode

Now configure VSCode to use the TealFlowMCP server with GitHub Copilot.

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS)
2. Type **"MCP: Add Server"** and select it
3. Choose **"Command"** as the server type
4. Enter the command: `uv --directory /absolute/path/to/TealFlowMCP run tealflow_mcp.py`

   **Replace `/absolute/path/to/TealFlowMCP` with the actual path from Step 2**

Or manually add this configuration:

```json
"tealflow-mcp": {
  "command": "uv",
  "args": [
    "--directory",
    "/absolute/path/to/TealFlowMCP",
    "run",
    "tealflow_mcp.py"
  ]
}
```

**Replace `/absolute/path/to/TealFlowMCP` with the actual path from Step 2**

#### Step 5: Restart VSCode

After saving the configuration, restart VSCode completely for the changes to take effect.

## Set Up Your Project

Create a new project directory where you'll build your Teal application:

```bash
mkdir my-teal-app
cd my-teal-app
```

### Copy Sample Data

**For PyPI installation:** The sample datasets are included in the package and can be accessed programmatically, or you can download them from the [GitHub repository](https://github.com/Appsilon/TealFlowMCP/tree/main/sample_data).

**For source installation:** Copy the sample clinical trial datasets from TealFlowMCP to your project:

```bash
cp -r /path/to/TealFlowMCP/sample_data ./
```

The sample data includes:
- `ADSL.Rds` - Subject-level analysis dataset
- `ADTTE.Rds` - Time-to-event analysis dataset
- `ADAE.Rds` - Adverse events analysis dataset
- `ADRS.Rds` - Response analysis dataset
- `ADQS.Rds` - Questionnaire analysis dataset

## R Setup

Ensure R is installed on your system. You don't need to manually install packages - TealFlowMCP includes a tool to set up the environment for you.

## Verify Everything Works

### Test the MCP Connection

1. Open VSCode in your project directory
2. Open GitHub Copilot Chat
3. Ask: **"List all clinical modules for survival analysis"**

If configured correctly, you should see Copilot use the `tealflow_search_modules_by_analysis` tool and return information about survival analysis modules like `tm_g_km`, `tm_t_coxreg`, and `tm_t_tte`.

### Generate Your First App

Try asking Copilot:

> "Build me a Teal app with a Kaplan-Meier plot for survival analysis."

Copilot will:
1. Verify the environment setup
2. Get the app template
3. Search for relevant modules
4. Check dataset compatibility
5. Generate complete working code in `app.R`

**Important!** Take into account that this process can take up to several minutes the first time the tool is called, as it needs to download and install several packages. Once the environment is properly set up and packages are installed, things should go faster.

### Run the App

Once generated, run your app in R:

```r
shiny::runApp()
```

Your Teal application should start in your default web browser!

## Troubleshooting

### MCP Tools Not Working

If Copilot isn't using the TealFlowMCP tools:

1. **Check the configuration file:**
   - Ensure the path is absolute, not relative
   - Verify the JSON syntax is correct (no trailing commas)
   - Make sure you're using forward slashes or escaped backslashes on Windows

2. **Restart VSCode completely:**
   - Close all VSCode windows
   - Reopen VSCode

3. **Verify installation:**

   For PyPI installation:
   ```bash
   python -c "import tealflow_mcp; print(f'TealFlowMCP version {tealflow_mcp.__version__}')"
   ```

   For source installation (verify uv is in PATH):
   ```bash
   which uv  # Linux/macOS
   where uv  # Windows
   ```

4. **Test the MCP server manually:**

   For PyPI installation:
   ```bash
   tealflow-mcp
   ```

   For source installation:
   ```bash
   cd /path/to/TealFlowMCP
   uv run tealflow_mcp.py
   ```
