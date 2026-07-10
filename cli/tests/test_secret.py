"""
Tests for lich secret command.
"""
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app
from lich.commands.secret import _generate_secret, _read_env_file, _write_env_file


class TestSecretHelpers:
    def test_generate_secret_alphanum_length(self):
        s = _generate_secret(32, "alphanum")
        assert len(s) == 32

    def test_generate_secret_alphanum_64(self):
        s = _generate_secret(64, "alphanum")
        assert len(s) == 64

    def test_generate_secret_unique(self):
        assert _generate_secret(32) != _generate_secret(32)

    def test_generate_secret_hex_format(self):
        s = _generate_secret(32, "hex")
        # token_hex(16) → 32 hex chars
        assert len(s) == 32
        assert all(c in "0123456789abcdef" for c in s)

    def test_generate_secret_urlsafe(self):
        s = _generate_secret(32, "urlsafe")
        # token_urlsafe returns base64url chars; length ≥ requested chars
        assert len(s) >= 32

    def test_generate_secret_full_charset(self):
        # 'full' charset includes punctuation
        s = _generate_secret(64, "full")
        assert len(s) == 64

    def test_env_file_roundtrip(self, temp_dir):
        env_path = temp_dir / ".env"
        _write_env_file(env_path, {"KEY1": "value1", "SECRET_KEY": "abc123"})
        loaded = _read_env_file(env_path)
        assert loaded["KEY1"] == "value1"
        assert loaded["SECRET_KEY"] == "abc123"

    def test_read_env_file_missing(self, temp_dir):
        result = _read_env_file(temp_dir / "nonexistent.env")
        assert result == {}

    def test_read_env_file_skips_comments(self, temp_dir):
        env_path = temp_dir / ".env"
        env_path.write_text("# comment\nKEY=val\n")
        result = _read_env_file(env_path)
        assert "KEY" in result
        assert len(result) == 1


class TestSecretCLI:
    def test_generate_single_secret(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "generate"])
        assert result.exit_code == 0

    def test_generate_multiple_secrets(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "generate", "-l", "16", "-c", "3"])
        assert result.exit_code == 0
        # Output table should contain 3 rows
        assert "1" in result.output
        assert "3" in result.output

    def test_generate_urlsafe_format(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "generate", "-f", "urlsafe"])
        assert result.exit_code == 0

    def test_check_missing_env_file(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "check", "-e", "nonexistent.env"])
        # should fail with exit 1 (file not found), never crash with traceback
        assert "Traceback" not in result.output
        assert result.exit_code == 1

    def test_check_weak_secrets(self, runner: CliRunner, in_lich_project):
        (in_lich_project / ".env").write_text("SECRET_KEY=changeme\n")
        result = runner.invoke(app, ["secret", "check", "-e", ".env"])
        # weak pattern found → exit 1
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_check_strong_secrets(self, runner: CliRunner, in_lich_project):
        strong = "a" * 32 + "1B2C3D4E5F6G7H8I9J0K"
        (in_lich_project / ".env").write_text(f"SECRET_KEY={strong}\n")
        result = runner.invoke(app, ["secret", "check", "-e", ".env"])
        assert result.exit_code == 0
        assert "All secrets look good" in result.output

    def test_rotate_missing_env_file(self, runner: CliRunner, in_lich_project):
        result = runner.invoke(app, ["secret", "rotate", "-e", "missing.env"])
        assert result.exit_code == 1
        assert "Traceback" not in result.output

    def test_secret_generate_help(self, runner: CliRunner):
        result = runner.invoke(app, ["secret", "generate", "--help"])
        assert result.exit_code == 0
