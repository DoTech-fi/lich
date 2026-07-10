"""Tests for safe subprocess helpers."""
from lich.commands._shell import run_local, run_remote, quote


class TestRunLocal:
    def test_runs_list_command(self):
        code, output = run_local(["echo", "hello"])
        assert code == 0
        assert "hello" in output

    def test_argument_with_metacharacters_is_not_interpreted(self):
        # If a shell were involved, this would create /tmp/lich_pwned.
        code, output = run_local(["echo", "hello; touch /tmp/lich_pwned"])
        assert code == 0
        assert "hello; touch /tmp/lich_pwned" in output
        import os
        assert not os.path.exists("/tmp/lich_pwned")

    def test_missing_command_returns_error_tuple(self):
        code, output = run_local(["definitely-not-a-real-command-xyz"])
        assert code == 1
        assert "not found" in output.lower()

    def test_timeout_returns_error_tuple(self):
        code, output = run_local(["sleep", "5"], timeout=1)
        assert code == 1
        assert "timeout" in output.lower()


class TestRunRemote:
    def test_builds_ssh_command_as_list(self, monkeypatch):
        captured = {}

        def fake_run_local(cmd, timeout=None, capture=True):
            captured["cmd"] = cmd
            return 0, "ok"

        monkeypatch.setattr("lich.commands._shell.run_local", fake_run_local)
        code, output = run_remote("prod-server", "docker ps")
        assert code == 0
        assert captured["cmd"][0] == "ssh"
        assert captured["cmd"][-1] == "docker ps"
        assert "prod-server" in captured["cmd"]


class TestQuote:
    def test_quote_neutralizes_injection(self):
        hostile = '/opt/app"; rm -rf / #'
        quoted = quote(hostile)
        # shlex.quote wraps in single quotes so the shell treats it as one token
        assert quoted.startswith("'")
        assert quoted.endswith("'")
