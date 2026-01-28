"""
Tests for setup_renv tool.
"""
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tealflow_mcp.core.enums import ResponseFormat
from tealflow_mcp.models import SetupRenvEnvironmentInput
from tealflow_mcp.tools.setup_renv import tealflow_setup_renv_environment


class TestSetupRenv(unittest.IsolatedAsyncioTestCase):
    """Tests for tealflow_setup_renv_environment."""

    def setUp(self):
        self.project_path = Path("/valid/project/path")

    @patch("tealflow_mcp.tools.setup_renv.Path.exists")
    async def test_invalid_path(self, mock_exists):
        """Test with non-existent path."""
        mock_exists.return_value = False
        
        params = SetupRenvEnvironmentInput(project_path="/invalid/path")
        result_json = await tealflow_setup_renv_environment(params)
        result = json.loads(result_json)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "filesystem_error")
        self.assertIn("does not exist", result["message"])

    @patch("tealflow_mcp.tools.setup_renv.subprocess.run")
    @patch("tealflow_mcp.tools.setup_renv.Path.exists")
    async def test_rscript_missing(self, mock_exists, mock_run):
        """Test when Rscript is missing."""
        mock_exists.return_value = True
        mock_run.side_effect = FileNotFoundError("Rscript not found")
        
        params = SetupRenvEnvironmentInput(project_path=str(self.project_path))
        result_json = await tealflow_setup_renv_environment(params)
        result = json.loads(result_json)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "rscript_not_found")
        self.assertIn("Rscript command not found", result["message"])

    @patch("tealflow_mcp.tools.setup_renv.subprocess.Popen")
    @patch("tealflow_mcp.tools.setup_renv.subprocess.run")
    @patch("tealflow_mcp.tools.setup_renv.Path.exists")
    @patch("tealflow_mcp.tools.setup_renv.Path.resolve")
    async def test_success_flow(self, mock_resolve, mock_exists, mock_run, mock_popen):
        """Test successful execution flow."""
        mock_resolve.return_value = self.project_path
        mock_exists.return_value = True
        
        # Mock Rscript --version check
        mock_run.return_value.returncode = 0
        
        # Mock Popen for R commands
        # We need to simulate 4 calls: 
        # 1. check/install renv
        # 2. init renv
        # 3. install packages
        # 4. snapshot
        
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("stdout output", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        params = SetupRenvEnvironmentInput(
            project_path=str(self.project_path),
            response_format=ResponseFormat.JSON
        )
        
        result_json = await tealflow_setup_renv_environment(params)
        result = json.loads(result_json)
        
        # Verify success
        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["error_type"])
        
        # Verify all steps completed
        expected_steps = [
            "renv_installed",
            "renv_initialized",
            "packages_installed",
            "snapshot_created"
        ]
        self.assertEqual(result["steps_completed"], expected_steps)
        
        # Verify tool called Rscript 4 times
        self.assertEqual(mock_popen.call_count, 4)

    @patch("tealflow_mcp.tools.setup_renv.subprocess.Popen")
    @patch("tealflow_mcp.tools.setup_renv.subprocess.run")
    @patch("tealflow_mcp.tools.setup_renv.Path.exists")
    @patch("tealflow_mcp.tools.setup_renv.Path.resolve")
    async def test_package_install_fail(self, mock_resolve, mock_exists, mock_run, mock_popen):
        """Test failure during package installation."""
        mock_resolve.return_value = self.project_path
        mock_exists.return_value = True
        
        # Mock Rscript --version check
        mock_run.return_value.returncode = 0
        
        # Setup mocking for Popen calls
        # 1. renv install -> Success (returncode 0)
        # 2. renv init -> Success (returncode 0)
        # 3. packages install -> Failure (returncode 1)
        
        process_success = MagicMock()
        process_success.communicate.return_value = ("success", "")
        process_success.returncode = 0
        
        process_fail = MagicMock()
        process_fail.communicate.return_value = ("pkg install start...", "Error installing package")
        process_fail.returncode = 1
        
        # side_effect iterates through return values for each call
        mock_popen.side_effect = [
            process_success, # renv check
            process_success, # renv init
            process_fail,    # packages install
        ]
        
        params = SetupRenvEnvironmentInput(project_path=str(self.project_path))
        result_json = await tealflow_setup_renv_environment(params)
        result = json.loads(result_json)
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "package_install_failed")
        self.assertIn("Failed to install required packages", result["message"])
        
        # Check logs captured
        self.assertIn("Error installing package", result["logs_excerpt"])
        
        # Check completed steps
        self.assertIn("renv_installed", result["steps_completed"])
        self.assertIn("renv_initialized", result["steps_completed"])
        self.assertNotIn("packages_installed", result["steps_completed"])
