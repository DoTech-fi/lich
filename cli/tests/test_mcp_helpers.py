"""
Tests for MCP shared helpers (sync + async runners).
"""
import pytest

from lich.mcp.tools import clean_cli_output, run_lich_command_async


class TestCleanOutput:
    def test_strips_ansi(self):
        assert clean_cli_output("\x1b[31mred\x1b[0m") == "red"

    def test_empty(self):
        assert clean_cli_output("") == ""


class TestAsyncRunner:
    @pytest.mark.asyncio
    async def test_success_returns_output(self):
        out = await run_lich_command_async(["python3", "-c", "print('async-ok')"])
        assert "async-ok" in out
        assert not out.startswith("ERROR")

    @pytest.mark.asyncio
    async def test_nonzero_exit_prefixed(self):
        out = await run_lich_command_async(
            ["python3", "-c", "import sys; print('boom'); sys.exit(2)"]
        )
        assert out.startswith("ERROR (exit 2):")
        assert "boom" in out

    @pytest.mark.asyncio
    async def test_missing_binary(self):
        out = await run_lich_command_async(["definitely-not-a-real-binary-xyz"])
        assert "not found" in out
