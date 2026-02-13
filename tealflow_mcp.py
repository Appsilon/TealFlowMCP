#!/usr/bin/env python3
"""
Teal Flow MCP Server - Entry Point

This is a backward-compatibility wrapper that allows running the server
directly from the project root during development.

For production use, the server is installed as a console script entry point
via pyproject.toml and runs from the tealflow_mcp package.
"""

from tealflow_mcp import main

if __name__ == "__main__":
    # Run the MCP server
    main()
