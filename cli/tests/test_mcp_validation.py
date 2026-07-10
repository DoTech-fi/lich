"""MCP tools must validate their arguments before touching the CLI/generators."""
import asyncio
import pytest

from lich.mcp.server import mcp


def _text_of(result) -> str:
    """Flatten a FastMCP call_tool result to a plain string.

    call_tool returns a tuple: (list[ContentBlock], dict).
    Concatenate all TextContent blocks into one string.
    """
    if isinstance(result, tuple):
        blocks, _ = result
        return " ".join(getattr(b, "text", str(b)) for b in blocks)
    return str(result)


@pytest.mark.asyncio
async def test_lich_make_entity_rejects_injection():
    result = await mcp.call_tool("lich_make_entity", {"name": "X; rm -rf /"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_make_service_rejects_injection():
    result = await mcp.call_tool("lich_make_service", {"name": "{__import__('os')}"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_migration_create_rejects_injection():
    result = await mcp.call_tool("lich_migration_create", {"message": "x; rm -rf /"})
    assert "Invalid name" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_secret_generate_rejects_huge_length():
    result = await mcp.call_tool("lich_secret_generate", {"length": 1000000})
    assert "length must be between" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_secret_generate_rejects_huge_count():
    result = await mcp.call_tool("lich_secret_generate", {"count": 5000})
    assert "count must be between" in _text_of(result)


@pytest.mark.asyncio
async def test_lich_git_tag_rejects_option_injection():
    """I1: lich_git_tag must reject a version that starts with '-' (option smuggling)."""
    result = await mcp.call_tool("lich_git_tag", {"version": "--delete"})
    text = _text_of(result)
    assert "Invalid" in text or "ERROR" in text


@pytest.mark.asyncio
async def test_lich_seed_rejects_injection():
    """M1: lich_seed must reject a name containing shell metacharacters."""
    result = await mcp.call_tool("lich_seed", {"name": "x; rm -rf /"})
    text = _text_of(result)
    assert "Invalid" in text or "ERROR" in text
