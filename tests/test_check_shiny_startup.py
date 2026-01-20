#!/usr/bin/env python3
"""
Test the check_shiny_startup tool.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

# Add parent directory to path so we can import tealflow_mcp
sys.path.insert(0, str(Path(__file__).parent.parent))

from tealflow_mcp import CheckShinyStartupInput, tealflow_check_shiny_startup


async def test_missing_file():
    """Test behavior when app.R doesn't exist."""
    print("\n=== Test 1: Missing app.R ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        params = CheckShinyStartupInput(app_path=tmpdir, timeout_seconds=5)
        result = await tealflow_check_shiny_startup(params)
        data = json.loads(result)
        print(f"Status: {data['status']}")
        print(f"Error Type: {data['error_type']}")
        print(f"Message: {data['message']}")
        assert data['status'] == 'error'
        assert data['error_type'] == 'file_not_found'


async def test_syntax_error():
    """Test behavior with syntax error in app.R."""
    print("\n=== Test 2: Syntax Error ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        app_file = Path(tmpdir) / "app.R"
        app_file.write_text("library(shiny)\nthis is not valid R syntax")
        
        params = CheckShinyStartupInput(app_path=tmpdir, timeout_seconds=5)
        result = await tealflow_check_shiny_startup(params)
        data = json.loads(result)
        print(f"Status: {data['status']}")
        print(f"Error Type: {data['error_type']}")
        print(f"Message: {data['message']}")
        assert data['status'] == 'error'
        assert data['error_type'] == 'syntax_error'


async def test_missing_package():
    """Test behavior with missing R package."""
    print("\n=== Test 3: Missing Package ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        app_file = Path(tmpdir) / "app.R"
        app_file.write_text("library(nonexistent_package_xyz123)")
        
        params = CheckShinyStartupInput(app_path=tmpdir, timeout_seconds=5)
        result = await tealflow_check_shiny_startup(params)
        data = json.loads(result)
        print(f"Status: {data['status']}")
        print(f"Error Type: {data['error_type']}")
        print(f"Message: {data['message']}")
        assert data['status'] == 'error'
        assert data['error_type'] == 'missing_package'


async def test_object_not_found():
    """Test behavior with undefined object."""
    print("\n=== Test 4: Object Not Found ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        app_file = Path(tmpdir) / "app.R"
        app_file.write_text("print(undefined_variable)")
        
        params = CheckShinyStartupInput(app_path=tmpdir, timeout_seconds=5)
        result = await tealflow_check_shiny_startup(params)
        data = json.loads(result)
        print(f"Status: {data['status']}")
        print(f"Error Type: {data['error_type']}")
        print(f"Message: {data['message']}")
        assert data['status'] == 'error'
        assert data['error_type'] == 'object_not_found'


async def test_simple_success():
    """Test behavior with simple successful R script."""
    print("\n=== Test 5: Simple Success ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        app_file = Path(tmpdir) / "app.R"
        app_file.write_text("print('Hello from R')\nquit()")
        
        params = CheckShinyStartupInput(app_path=tmpdir, timeout_seconds=5)
        result = await tealflow_check_shiny_startup(params)
        data = json.loads(result)
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        print(f"Logs excerpt (first 100 chars): {data['logs_excerpt'][:100]}")
        assert data['status'] == 'ok'


async def main():
    """Run all tests."""
    print("Testing check_shiny_startup tool...")
    
    try:
        await test_missing_file()
        await test_syntax_error()
        await test_missing_package()
        await test_object_not_found()
        await test_simple_success()
        
        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
