"""Tests for the shared run_lich_command helper."""
from unittest.mock import MagicMock

from lich.mcp.tools import run_lich_command


def _mock_result(returncode: int, stdout: str = "", stderr: str = ""):
    res = MagicMock()
    res.returncode = returncode
    res.stdout = stdout
    res.stderr = stderr
    return res


def test_success_returns_clean_output(mocker):
    mocker.patch("subprocess.run", return_value=_mock_result(0, stdout="all good\n"))
    assert run_lich_command(["lich", "routes"]) == "all good\n"


def test_failure_is_prefixed_with_error_and_exit_code(mocker):
    mocker.patch("subprocess.run", return_value=_mock_result(2, stderr="boom\n"))
    output = run_lich_command(["lich", "deploy", "prod", "web"])
    assert output.startswith("ERROR (exit 2):")
    assert "boom" in output


def test_missing_binary_message(mocker):
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)
    assert run_lich_command(["lich", "routes"]) == "lich command not found"
