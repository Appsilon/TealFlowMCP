"""
Snapshot Renv Environment tool implementation.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from ..models import SnapshotRenvEnvironmentInput
from ..core.enums import ResponseFormat

def _run_r_command(command: str, cwd: Path, timeout: int = 300) -> tuple[int, str, str]:
    """Run an R command using Rscript -e."""
    env = os.environ.copy()

    try:
        process = subprocess.Popen(
            ["Rscript", "-e", command],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise TimeoutError("Command timed out")
    except FileNotFoundError:
        # This means Rscript is not found
        raise FileNotFoundError("Rscript not found")

def _format_markdown_response(result: dict[str, Any]) -> str:
    """Format the result as a Markdown report."""
    status_emoji = "✅" if result["status"] == "ok" else "❌"

    md = f"# {status_emoji} Snapshot Environment: {result['status'].upper()}\n\n"

    if result["status"] == "error":
        md += f"**Error Type:** `{result['error_type']}`\n\n"

    md += f"**Message:** {result['message']}\n\n"

    if result.get("logs_excerpt") and result["logs_excerpt"].strip():
        md += "### Snapshot Logs\n"
        md += "```\n"
        md += result["logs_excerpt"]
        md += "\n```\n"

    return md

async def tealflow_snapshot_renv_environment(params: SnapshotRenvEnvironmentInput) -> str:
    """
    Create an renv snapshot of the current R project environment.

    This captures the current state of installed packages and records them in renv.lock.
    """
    project_path = Path(params.project_path).resolve()
    logs = []

    # helper to append logs
    def log_output(stdout: str, stderr: str):
        if stdout.strip():
            logs.append(f"STDOUT:\n{stdout.strip()}")
        if stderr.strip():
            logs.append(f"STDERR:\n{stderr.strip()}")

    try:
        # STEP 1: Validate Project Path
        if not project_path.exists():
            return json.dumps({
                "status": "error",
                "error_type": "filesystem_error",
                "message": f"Project path does not exist: {project_path}",
                "logs_excerpt": ""
            }, indent=2)

        # STEP 2: Ensure Rscript Exists
        try:
            subprocess.run(["Rscript", "--version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
             return json.dumps({
                "status": "error",
                "error_type": "rscript_not_found",
                "message": "Rscript command not found. Please install R.",
                "logs_excerpt": ""
            }, indent=2)

        # STEP 3: Check if renv is initialized
        renv_dir = project_path / "renv"
        if not renv_dir.exists():
            return json.dumps({
                "status": "error",
                "error_type": "renv_not_initialized",
                "message": f"renv is not initialized in this project. Please run tealflow_setup_renv_environment first.",
                "logs_excerpt": ""
            }, indent=2)

        # STEP 4: Snapshot Environment
        snapshot_cmd = 'renv::snapshot(prompt = FALSE)'
        try:
            rc, out, err = _run_r_command(snapshot_cmd, project_path)
            log_output(out, err)
            if rc != 0:
                return json.dumps({
                    "status": "error",
                    "error_type": "snapshot_failed",
                    "message": "Failed to create renv snapshot.",
                    "logs_excerpt": "\n".join(logs)
                }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error_type": "snapshot_failed",
                "message": f"Exception creating snapshot: {str(e)}",
                "logs_excerpt": "\n".join(logs)
            }, indent=2)

        # Success
        result = {
            "status": "ok",
            "error_type": None,
            "message": "Renv snapshot created successfully.",
            "logs_excerpt": "\n".join(logs)[-2000:] # Truncate logs if too long
        }

        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_markdown_response(result)

        return json.dumps(result, indent=2)

    except Exception as e:
        # Catch-all
        return json.dumps({
            "status": "error",
            "error_type": "execution_error",
            "message": f"Unexpected error: {str(e)}",
            "logs_excerpt": "\n".join(logs)
        }, indent=2)
