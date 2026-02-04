"""
Helper utilities for running R commands.
"""

import os
import subprocess
from pathlib import Path


def _run_r_command(command: str, cwd: Path, timeout: int = 300) -> tuple[int, str, str]:
    """
    Run an R command using Rscript -e.

    Args:
        command: R code to execute
        cwd: Working directory for the R process
        timeout: Maximum time to wait for command completion (seconds)

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        TimeoutError: If command execution exceeds timeout
        FileNotFoundError: If Rscript is not found in PATH
    """
    env = os.environ.copy()

    try:
        process = subprocess.Popen(
            ["Rscript", "-e", command],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise TimeoutError("Command timed out") from None
    except FileNotFoundError:
        # This means Rscript is not found
        raise FileNotFoundError("Rscript not found") from None


def _get_r_help(function_name: str, package: str | None = None) -> str:
    """
    Get help documentation for an R function.

    Args:
        function_name: Name of the R function to get help for
        package: Optional package name to search in (e.g., "base", "stats", "shiny")

    Returns:
        String containing the help documentation for the function

    Raises:
        FileNotFoundError: If Rscript is not found in PATH
        ValueError: If the function or package is not found in R
    """
    # Build the R command to get help
    if package:
        r_command = f"?{package}::{function_name}"
    else:
        r_command = f"?{function_name}"

    # Use a temporary directory as cwd since we don't need a specific working directory
    cwd = Path.cwd()

    try:
        returncode, stdout, stderr = _run_r_command(r_command, cwd, timeout=30)

        # Check if help was not found (R returns exit code 0 even when not found)
        if "No documentation for" in stdout or "No documentation for" in stderr:
            if package:
                raise ValueError(f"Help for '{function_name}' not found in package '{package}'")
            else:
                raise ValueError(f"Help for '{function_name}' not found")

        if returncode != 0:
            # Some other error occurred
            if package:
                raise ValueError(f"Help for '{function_name}' not found in package '{package}'")
            else:
                raise ValueError(f"Help for '{function_name}' not found")

        return stdout.strip()

    except TimeoutError:
        raise TimeoutError("Command timed out while retrieving help") from None
    except FileNotFoundError:
        raise FileNotFoundError("Rscript not found") from None
