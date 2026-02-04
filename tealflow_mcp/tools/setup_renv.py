"""
Setup Renv Environment tool implementation.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

from ..core.enums import ResponseFormat
from ..models import SetupRenvEnvironmentInput
from ..utils import _run_r_command


def _format_markdown_response(result: dict[str, Any]) -> str:
    """Format the result as a Markdown report."""
    status_emoji = "✅" if result["status"] == "ok" else "❌"

    md = f"# {status_emoji} Setup Environment: {result['status'].upper()}\n\n"

    if result["status"] == "error":
        md += f"**Error Type:** `{result['error_type']}`\n\n"

    md += f"**Message:** {result['message']}\n\n"

    if result.get("steps_completed"):
        md += "### Steps Completed\n"
        for step in result["steps_completed"]:
            md += f"- {step}\n"
        md += "\n"

    if result.get("logs_excerpt") and result["logs_excerpt"].strip():
        md += "### Implementation Logs\n"
        md += "```\n"
        md += result["logs_excerpt"]
        md += "\n```\n"

    return md


async def tealflow_setup_renv_environment(params: SetupRenvEnvironmentInput) -> str:
    """
    Prepare an R project directory so it is ready to run Teal Shiny applications.
    """
    project_path = Path(params.project_path).resolve()
    steps_completed: list[str] = []
    logs: list[str] = []

    # helper to append logs
    def log_output(stdout: str, stderr: str):
        if stdout.strip():
            logs.append(f"STDOUT:\n{stdout.strip()}")
        if stderr.strip():
            logs.append(f"STDERR:\n{stderr.strip()}")

    try:
        # STEP 1: Validate Project Path
        if not project_path.exists():
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "filesystem_error",
                    "steps_completed": steps_completed,
                    "message": f"Project path does not exist: {project_path}",
                    "logs_excerpt": "",
                },
                indent=2,
            )

        # STEP 2: Ensure Rscript Exists
        try:
            subprocess.run(["Rscript", "--version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "rscript_not_found",
                    "steps_completed": steps_completed,
                    "message": "Rscript command not found. Please install R.",
                    "logs_excerpt": "",
                },
                indent=2,
            )

        # STEP 3: Install renv if Missing
        # Use configured repos if available, fall back to CRAN only if not configured
        check_renv_cmd = """
if (!requireNamespace("renv", quietly = TRUE)) {
  repos <- getOption("repos")
  if (is.null(repos) || identical(repos, c(CRAN = "@CRAN@")) || all(repos == "")) {
    repos <- "https://cloud.r-project.org"
  }
  install.packages("renv", repos = repos)
}
"""
        try:
            rc, out, err = _run_r_command(check_renv_cmd, project_path)
            log_output(out, err)
            if rc != 0:
                return json.dumps(
                    {
                        "status": "error",
                        "error_type": "renv_install_failed",
                        "steps_completed": steps_completed,
                        "message": "Failed to install renv package.",
                        "logs_excerpt": "\n".join(logs),
                    },
                    indent=2,
                )
            steps_completed.append("renv_installed")
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "renv_install_failed",
                    "steps_completed": steps_completed,
                    "message": f"Exception installing renv: {e!s}",
                    "logs_excerpt": "\n".join(logs),
                },
                indent=2,
            )

        # STEP 4: Initialize renv in Project
        # If lockfile exists, restore packages (also activates renv).
        # If not, initialize a bare environment.
        init_renv_cmd = 'if (!file.exists("renv.lock")) renv::init(bare = TRUE) else renv::restore(prompt = FALSE)'

        try:
            rc, out, err = _run_r_command(init_renv_cmd, project_path)
            log_output(out, err)
            if rc != 0:
                return json.dumps(
                    {
                        "status": "error",
                        "error_type": "renv_install_failed",  # Using renv_install_failed for init failure as well based on steps? Or maybe execution_error? Instructions say renv_install_failed for step 3 and 4 failure.
                        "steps_completed": steps_completed,
                        "message": "Failed to initialize renv.",
                        "logs_excerpt": "\n".join(logs),
                    },
                    indent=2,
                )
            steps_completed.append("renv_initialized")
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "renv_install_failed",
                    "steps_completed": steps_completed,
                    "message": f"Exception initializing renv: {e!s}",
                    "logs_excerpt": "\n".join(logs),
                },
                indent=2,
            )

        # STEP 5: Install Required Packages
        # Only install packages that are missing from the lockfile.
        # If no lockfile exists (fresh project), install all required packages.
        install_pkgs_cmd = """
required_packages <- c("shiny", "teal", "teal.modules.general", "teal.modules.clinical")

if (file.exists("renv.lock")) {
  lockfile <- renv::lockfile_read("renv.lock")
  locked_pkgs <- names(lockfile$Packages)
  missing <- setdiff(required_packages, locked_pkgs)
  if (length(missing) > 0) {
    renv::install(missing, prompt = FALSE)
  }
} else {
  renv::install(required_packages, prompt = FALSE)
}
"""
        try:
            rc, out, err = _run_r_command(install_pkgs_cmd, project_path, timeout=600)
            log_output(out, err)
            if rc != 0:
                return json.dumps(
                    {
                        "status": "error",
                        "error_type": "package_install_failed",
                        "steps_completed": steps_completed,
                        "message": "Failed to install required packages.",
                        "logs_excerpt": "\n".join(logs),
                    },
                    indent=2,
                )
            steps_completed.append("packages_installed")
        except TimeoutError:
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "package_install_failed",
                    "steps_completed": steps_completed,
                    "message": "Package installation timed out.",
                    "logs_excerpt": "\n".join(logs),
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error_type": "package_install_failed",
                    "steps_completed": steps_completed,
                    "message": f"Exception installing packages: {e!s}",
                    "logs_excerpt": "\n".join(logs),
                },
                indent=2,
            )

        # Success
        result = {
            "status": "ok",
            "error_type": None,
            "steps_completed": steps_completed,
            "message": "Renv environment set up successfully.",
            "logs_excerpt": "\n".join(logs)[-2000:],  # Truncate logs if too long
        }

        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_markdown_response(result)

        return json.dumps(result, indent=2)

    except Exception as e:
        # Catch-all
        return json.dumps(
            {
                "status": "error",
                "error_type": "execution_error",
                "steps_completed": steps_completed,
                "message": f"Unexpected error: {e!s}",
                "logs_excerpt": "\n".join(logs),
            },
            indent=2,
        )
