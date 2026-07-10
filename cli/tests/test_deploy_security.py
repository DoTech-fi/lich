"""Security tests for lich deploy: no shell=True, validated inputs, quoted scripts."""
import pytest


class TestVerifyGithubAccess:
    def test_uses_list_command_not_shell(self, monkeypatch):
        """A hostile key_path must be passed as a literal argument, never through a shell."""
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["kwargs"] = kwargs

            class Result:
                returncode = 1
                stdout = ""
                stderr = "Hi acme! You've successfully authenticated"

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        hostile_key = '/tmp/key"; touch /tmp/lich_pwned #'
        result = _verify_github_access("git@github.com:acme/app.git", hostile_key)

        assert isinstance(captured["cmd"], list), "command must be an argument list"
        assert captured["kwargs"].get("shell") is not True, "shell=True is forbidden"
        assert hostile_key in captured["cmd"], "key path must be a literal list element"
        assert result is True

    def test_detects_failed_auth(self, monkeypatch):
        def fake_run(cmd, **kwargs):
            class Result:
                returncode = 255
                stdout = ""
                stderr = "git@github.com: Permission denied (publickey)."

            return Result()

        monkeypatch.setattr("lich.commands.deploy.subprocess.run", fake_run)
        from lich.commands.deploy import _verify_github_access

        assert _verify_github_access("git@github.com:acme/app.git", "/tmp/key") is False
