# TealFlowMCP Documentation

This directory contains the source files for the TealFlowMCP documentation website, built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

Complete documentation for TealFlowMCP - an MCP server for building Teal R Shiny applications.

## 📚 View Documentation Online

**Live Documentation**: [https://appsilon.github.io/TealFlowMCP/](https://appsilon.github.io/TealFlowMCP/)

## Local Development

### Prerequisites

Install documentation dependencies:

```bash
# Install using uv
uv sync --group docs

# Or install directly with pip
pip install mkdocs-material mkdocstrings[python] mkdocs-minify-plugin mkdocs-git-revision-date-localized-plugin
```

### Build and Serve Locally

```bash
# Serve documentation locally with live reload
mkdocs serve

# Open browser to http://127.0.0.1:8000/
```

### Build Static Site

```bash
# Build static HTML files to site/ directory
mkdocs build

# Build with strict mode (fails on warnings)
mkdocs build --strict
```

## Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the `main` branch via the [docs workflow](../.github/workflows/docs.yml).

### Manual Deployment

```bash
mkdocs gh-deploy
```

## Documentation Files

### [TOOLS.md](TOOLS.md)
Complete reference for all 10 MCP tools provided by TealFlowMCP:
- Module discovery and search tools
- Code generation tools
- Dataset management tools
- Environment setup and validation tools

Each tool includes:
- Description and purpose
- Parameter specifications
- Usage examples
- Response formats

### [CONFIGURATION.md](CONFIGURATION.md)
Guide for setting up and using TealFlowMCP:
- MCP client configuration (Claude Desktop, GitHub Copilot, Cursor, etc.)
- Getting started workflow
- Usage patterns and examples
- Frequently Asked Questions (FAQ)
- Troubleshooting tips

### [QUICKSTART.md](QUICKSTART.md)
Step-by-step quickstart guide for VSCode and GitHub Copilot users.

## Other Resources

### [../CLAUDE.md](../CLAUDE.md)
Developer guide for contributors using Claude Code.

## Quick Links

- **Installation**: See main [README.md](../README.md#installation)
- **Testing**: See main [README.md](../README.md#testing)
- **Code Quality**: See main [README.md](../README.md#code-quality)
- **Contributing**: Check project structure in [CLAUDE.md](../CLAUDE.md)

## Key Concepts

**MCP (Model Context Protocol)**: Framework that enables LLMs to use external tools and data sources.

**Teal**: R framework for building interactive Shiny applications for clinical trial data analysis.

**ADaM Datasets**: CDISC Analysis Data Model - standard format for clinical trial analysis datasets (ADSL, ADTTE, ADAE, etc.).

**renv**: R package for creating reproducible R environments with locked package versions.

## Need Help?

1. Check the [FAQ section](CONFIGURATION.md#frequently-asked-questions) in CONFIGURATION.md
2. Review [usage examples](CONFIGURATION.md#usage-patterns) in CONFIGURATION.md
3. Consult the [tool reference](TOOLS.md) for specific tool details
4. Follow the [Quickstart Guide](QUICKSTART.md) for initial setup
