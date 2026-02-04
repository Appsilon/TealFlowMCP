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
