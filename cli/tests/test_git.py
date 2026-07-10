"""
Tests for lich git commands (commit/tag/push).
"""
import inspect
from unittest.mock import patch
from typer.testing import CliRunner

from lich.cli import app
import lich.commands.git as git_mod


class TestGitCLI:
    def test_commit_help(self, runner: CliRunner):
        result = runner.invoke(app, ["commit", "--help"])
        assert result.exit_code == 0
        assert "commit" in result.output.lower() or "message" in result.output.lower()

    def test_tag_help(self, runner: CliRunner):
        result = runner.invoke(app, ["tag", "--help"])
        assert result.exit_code == 0

    def test_push_help(self, runner: CliRunner):
        result = runner.invoke(app, ["push", "--help"])
        assert result.exit_code == 0

    def test_commit_with_empty_message_exits_1(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["commit", "-m", ""])
        # Empty message should exit 1 (guard prevents git option smuggling)
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_commit_with_dash_prefix_exits_1(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["commit", "-m", "--inject"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_commit_with_message_calls_git(self, runner: CliRunner, in_lich_project):
        """Commit with valid message calls underlying git command."""
        with patch.object(git_mod, "_run_command", return_value=(0, "1 file changed", "")) as mock_run:
            result = runner.invoke(app, ["commit", "-m", "feat: add feature"])
        assert "Traceback" not in result.output
        # _run_command should have been called with git commit
        assert mock_run.called

    def test_commit_git_failure_exits_1(self, runner: CliRunner, in_lich_project):
        with patch.object(git_mod, "_run_command", return_value=(1, "", "nothing to commit")):
            result = runner.invoke(app, ["commit", "-m", "feat: test"])
        assert result.exit_code == 1

    def test_push_git_failure_exits_1(self, runner: CliRunner, in_lich_project):
        with patch.object(git_mod, "_run_command", return_value=(128, "", "fatal: not a git repo")):
            result = runner.invoke(app, ["push"])
        assert result.exit_code == 1

    def test_push_git_success(self, runner: CliRunner, in_lich_project):
        with patch.object(git_mod, "_run_command", return_value=(0, "Everything up-to-date", "")):
            result = runner.invoke(app, ["push"])
        assert result.exit_code == 0
        assert "Traceback" not in result.output


class TestGitModuleDedup:
    def test_no_local_run_command_copy(self):
        """Dedup regression guard: git.py must use common.run_command, not define its own."""
        src = inspect.getsource(git_mod)
        assert "def _run_command" not in src

    def test_imports_run_command_from_common(self):
        """Verify the imported _run_command is indeed common.run_command."""
        from lich.commands.common import run_command
        assert git_mod._run_command is run_command
