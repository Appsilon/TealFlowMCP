"""
Check Shiny startup tool implementation.

Validates that a Shiny app.R file can start without errors.
"""

import json
import os
import re
import subprocess
from pathlib import Path

from ..models import CheckShinyStartupInput


def _classify_error(stderr_output: str, stdout_output: str) -> tuple[str | None, str]:
    """
    Classify the type of error from R output.
    
    Args:
        stderr_output: Standard error output from R process
        stdout_output: Standard output from R process
    
    Returns:
        Tuple of (error_type, message)
    """
    combined = stderr_output + "\n" + stdout_output
    
    # Check for missing packages
    if re.search(r"there is no package called|could not find package", combined, re.IGNORECASE):
        package_match = re.search(r"package called ['\"]([^'\"]+)['\"]", combined)
        if package_match:
            return "missing_package", f"Missing R package: {package_match.group(1)}"
        return "missing_package", "Missing R package"
    
    # Check for syntax errors
    if re.search(r"unexpected|syntax error", combined, re.IGNORECASE):
        return "syntax_error", "R syntax error in app.R"
    
    # Check for object not found
    if re.search(r"object .* not found|Error in .* : object", combined, re.IGNORECASE):
        obj_match = re.search(r"object ['\"]?([^'\" ]+)['\"]? not found", combined)
        if obj_match:
            return "object_not_found", f"Object not found: {obj_match.group(1)}"
        return "object_not_found", "Object not found"
    
    # Check for connection/network errors
    if re.search(r"cannot open the connection|could not resolve host", combined, re.IGNORECASE):
        return "connection_error", "Network or file connection error"
    
    # Generic error
    if re.search(r"Error|error:", combined):
        # Try to extract a meaningful error message
        error_match = re.search(r"Error[:\s]+([^\n]+)", combined)
        if error_match:
            return "execution_error", error_match.group(1).strip()
        return "execution_error", "R execution error"
    
    return None, "Unknown error"


def _get_log_excerpt(stdout: str, stderr: str, max_lines: int = 30) -> str:
    """
    Extract relevant log excerpt from output.
    
    Args:
        stdout: Standard output
        stderr: Standard error
        max_lines: Maximum number of lines to include
    
    Returns:
        Formatted log excerpt
    """
    # Combine outputs
    combined = ""
    if stderr.strip():
        combined += "=== STDERR ===\n" + stderr.strip() + "\n\n"
    if stdout.strip():
        combined += "=== STDOUT ===\n" + stdout.strip()
    
    if not combined.strip():
        return "No output captured"
    
    # Take last N lines
    lines = combined.split("\n")
    if len(lines) > max_lines:
        lines = ["... (output truncated) ..."] + lines[-max_lines:]
    
    return "\n".join(lines)


async def tealflow_check_shiny_startup(params: CheckShinyStartupInput) -> str:
    """
    Check if a Shiny app starts without errors.
    
    Runs Rscript app.R in the specified directory with a timeout,
    captures output, and returns structured information about startup status.
    
    Args:
        params: Input parameters (app_path, timeout_seconds)
    
    Returns:
        JSON string with status, error_type, message, and logs_excerpt
    """
    try:
        # Resolve app path
        app_path = Path(params.app_path).resolve()
        app_file = app_path / "app.R"
        
        # Validate app.R exists
        if not app_file.exists():
            result = {
                "status": "error",
                "error_type": "file_not_found",
                "message": f"app.R not found at {app_file}",
                "logs_excerpt": f"Expected file: {app_file}\nDirectory contents: {list(app_path.glob('*')) if app_path.exists() else 'directory does not exist'}"
            }
            return json.dumps(result, indent=2)
        
        # Run Rscript with timeout
        try:
            process = subprocess.Popen(
                ["Rscript", "app.R"],
                cwd=str(app_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "R_BROWSER": "false"}  # Prevent browser from opening
            )
            
            # Wait with timeout
            try:
                stdout, stderr = process.communicate(timeout=params.timeout_seconds)
            except subprocess.TimeoutExpired:
                # Timeout reached - this could be success (app running) or hanging
                process.kill()
                stdout, stderr = process.communicate()
                
                # Check if app successfully started before timeout
                combined_output = stdout + stderr
                if re.search(r"Listening on|Starting Shiny", combined_output, re.IGNORECASE):
                    result = {
                        "status": "ok",
                        "error_type": None,
                        "message": "App started successfully (reached listening state)",
                        "logs_excerpt": _get_log_excerpt(stdout, stderr, max_lines=20)
                    }
                else:
                    result = {
                        "status": "error",
                        "error_type": "timeout",
                        "message": f"App did not start within {params.timeout_seconds} seconds",
                        "logs_excerpt": _get_log_excerpt(stdout, stderr)
                    }
                return json.dumps(result, indent=2)
            
            # Process completed within timeout
            # Check for successful startup indicators
            combined_output = stdout + stderr
            
            if process.returncode == 0 or re.search(r"Listening on|Starting Shiny", combined_output, re.IGNORECASE):
                result = {
                    "status": "ok",
                    "error_type": None,
                    "message": "App started successfully",
                    "logs_excerpt": _get_log_excerpt(stdout, stderr, max_lines=20)
                }
            else:
                # Process exited with error
                error_type, error_message = _classify_error(stderr, stdout)
                result = {
                    "status": "error",
                    "error_type": error_type,
                    "message": error_message,
                    "logs_excerpt": _get_log_excerpt(stdout, stderr)
                }
            
            return json.dumps(result, indent=2)
            
        except FileNotFoundError:
            result = {
                "status": "error",
                "error_type": "rscript_not_found",
                "message": "Rscript command not found. Is R installed?",
                "logs_excerpt": "Cannot execute Rscript. Please ensure R is installed and in PATH."
            }
            return json.dumps(result, indent=2)
    
    except Exception as e:
        result = {
            "status": "error",
            "error_type": "internal_error",
            "message": f"Internal error: {str(e)}",
            "logs_excerpt": str(e)
        }
        return json.dumps(result, indent=2)
