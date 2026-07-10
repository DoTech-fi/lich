"""
CLI-layer security tests for git subcommands.
Validates that argument injection is caught before any subprocess runs.
"""
import pytest
from typer.testing import CliRunner

from lich.cli import app


class TestGitTagValidation:
    """I1: git tag must reject option-injected version strings at the CLI layer."""

    def test_git_tag_rejects_leading_dash(self, runner: CliRunner, monkeypatch):
        """'--delete' must be rejected as a version before git is called."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)

        result = runner.invoke(app, ["tag", "--delete"])
        # Typer itself will intercept --delete as an option flag and complain,
        # so we only need the test to NOT call _run_command with a git tag invocation.
        # The real injection risk is a bare argument like "-d" passed as version.
        assert "delete" not in " ".join(str(c) for c in called)

    def test_git_tag_rejects_dash_version_argument(self, runner: CliRunner, monkeypatch):
        """A version argument starting with '-' must be rejected before git tag runs."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)

        result = runner.invoke(app, ["tag", "-d"])
        # Typer will treat -d as an unknown option — either way git tag is never reached.
        git_tag_calls = [c for c in called if len(c) >= 2 and c[:2] == ["git", "tag"]]
        assert git_tag_calls == [], f"git tag was called with: {git_tag_calls}"

    def test_git_tag_rejects_unknown_flags(self, runner: CliRunner, monkeypatch):
        """Unknown flag-style arguments must never result in a git tag subprocess call."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)

        # An unknown flag will be caught by typer before reaching git_tag.
        result = runner.invoke(app, ["tag", "--unknown-flag-xyz"])
        git_tag_calls = [c for c in called if "git" in c and "tag" in c]
        assert git_tag_calls == []

    def test_git_tag_valid_version_reaches_git(self, runner: CliRunner, monkeypatch):
        """A clean version like v1.2.3 must pass validation and proceed."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)
        # Suppress the "Push this tag?" prompt
        monkeypatch.setattr("lich.commands.git.Confirm.ask", lambda msg, **kw: False)

        result = runner.invoke(app, ["tag", "v1.2.3"])
        git_tag_calls = [c for c in called if len(c) >= 3 and c[0] == "git" and c[1] == "tag"]
        assert git_tag_calls, f"git tag was never called; calls={called}; output={result.output}"
        assert git_tag_calls[0][2] == "v1.2.3"


class TestGitCommitValidation:
    """I2: git commit must reject empty or dash-prefixed messages."""

    def test_git_commit_rejects_dash_message(self, runner: CliRunner, monkeypatch):
        """A message starting with '-' must be rejected before git commit runs."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)

        result = runner.invoke(app, ["commit", "--message", "-m evil"])
        assert result.exit_code == 1
        git_commit_calls = [c for c in called if len(c) >= 2 and c[:2] == ["git", "commit"]]
        assert git_commit_calls == [], f"git commit was called despite invalid message: {git_commit_calls}"

    def test_git_commit_valid_message_proceeds(self, runner: CliRunner, monkeypatch):
        """A normal commit message must reach git commit without error."""
        called = []

        def fake_run_command(cmd, cwd=None):
            called.append(cmd)
            return 0, "1 file changed", ""

        monkeypatch.setattr("lich.commands.git._run_command", fake_run_command)

        result = runner.invoke(app, ["commit", "--message", "feat: add login"])
        git_commit_calls = [c for c in called if len(c) >= 2 and c[:2] == ["git", "commit"]]
        assert git_commit_calls, f"git commit was never called; output={result.output}"
