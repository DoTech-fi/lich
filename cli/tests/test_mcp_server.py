import pytest
from lich.mcp.server import mcp

# All 47 expected tools from our MCP implementation
ALL_EXPECTED_TOOLS = [
    # Project tools (2)
    "lich_init",
    "lich_check_project",
    # Make tools (10)
    "lich_make_service",
    "lich_make_entity",
    "lich_make_api",
    "lich_make_dto",
    "lich_make_factory",
    "lich_make_middleware",
    "lich_make_event",
    "lich_make_listener",
    "lich_make_job",
    "lich_make_policy",
    # Git tools (3)
    "lich_git_commit",
    "lich_git_tag",
    "lich_git_push",
    # QA tools (4)
    "lich_lint_backend",
    "lich_lint_frontend",
    "lich_security_scan",
    "lich_test",
    # Ops tools (2)
    "lich_deploy",
    "lich_backup",
    # Routes tools (1)
    "lich_routes",
    # Seed tools (2)
    "lich_seed",
    "lich_seed_list",
    # Migration tools (6)
    "lich_migration_init",
    "lich_migration_create",
    "lich_migration_up",
    "lich_migration_down",
    "lich_migration_status",
    "lich_migration_heads",
    # Secret tools (3)
    "lich_secret_generate",
    "lich_secret_rotate",
    "lich_secret_check",
    # Production tools (2)
    "lich_production_ready_check",
    "lich_production_ready_fix",
    # CI tools (4)
    "lich_ci_all",
    "lich_ci_backend",
    "lich_ci_web",
    "lich_ci_admin",
    # Middleware tools (3)
    "lich_middleware_list",
    "lich_middleware_enable",
    "lich_middleware_disable",
    # Dev tools (2)
    "lich_dev_start",
    "lich_dev_stop",
    # Utility tools (3)
    "lich_adopt",
    "lich_upgrade",
    "lich_version",
]

EXPECTED_TOOL_COUNT = 47


def test_all_mcp_tools_registered():
    """Verify that ALL 47 Lich tools are registered in the MCP server."""
    
    try:
        tools = [t.name for t in mcp._tool_manager.list_tools()]
    except AttributeError:
        pytest.skip("Could not access internal tool registry")
    
    print(f"\nRegistered Tools ({len(tools)}):")
    for t in sorted(tools):
        print(f"  - {t}")
    
    # Check we have exactly 47 tools
    assert len(tools) == EXPECTED_TOOL_COUNT, f"Expected {EXPECTED_TOOL_COUNT} tools, found {len(tools)}"
    
    # Check each expected tool exists
    for tool in ALL_EXPECTED_TOOLS:
        assert tool in tools, f"Missing tool: {tool}"


def test_mcp_tools_have_descriptions():
    """Verify that each MCP tool has a docstring/description."""
    
    try:
        tools = mcp._tool_manager.list_tools()
    except AttributeError:
        pytest.skip("Could not access internal tool registry")
    
    for tool in tools:
        assert tool.description, f"Tool '{tool.name}' is missing description"
        print(f"  {tool.name}: {tool.description[:50]}...")


def test_mcp_tools_are_callable():
    """Verify that each registered tool has a callable function."""
    
    try:
        tools = mcp._tool_manager.list_tools()
    except AttributeError:
        pytest.skip("Could not access internal tool registry")
    
    for tool in tools:
        assert callable(tool.fn), f"Tool '{tool.name}' is not callable"


class TestMCPToolCategories:
    """Test that tools are properly grouped by category."""
    
    def test_project_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        project_tools = ["lich_init", "lich_check_project"]
        for t in project_tools:
            assert t in tools
    
    def test_make_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        make_tools = [
            "lich_make_service", "lich_make_entity", "lich_make_api",
            "lich_make_dto", "lich_make_factory", "lich_make_middleware",
            "lich_make_event", "lich_make_listener", "lich_make_job",
            "lich_make_policy"
        ]
        for t in make_tools:
            assert t in tools
    
    def test_git_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        git_tools = ["lich_git_commit", "lich_git_tag", "lich_git_push"]
        for t in git_tools:
            assert t in tools
    
    def test_qa_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        qa_tools = ["lich_lint_backend", "lich_lint_frontend", "lich_security_scan", "lich_test"]
        for t in qa_tools:
            assert t in tools
    
    def test_ops_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        ops_tools = ["lich_deploy", "lich_backup"]
        for t in ops_tools:
            assert t in tools
    
    def test_routes_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        assert "lich_routes" in tools
    
    def test_seed_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        seed_tools = ["lich_seed", "lich_seed_list"]
        for t in seed_tools:
            assert t in tools
    
    def test_migration_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        migration_tools = [
            "lich_migration_init", "lich_migration_create", 
            "lich_migration_up", "lich_migration_down",
            "lich_migration_status", "lich_migration_heads"
        ]
        for t in migration_tools:
            assert t in tools
    
    def test_secret_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        secret_tools = ["lich_secret_generate", "lich_secret_rotate", "lich_secret_check"]
        for t in secret_tools:
            assert t in tools
    
    def test_production_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        production_tools = ["lich_production_ready_check", "lich_production_ready_fix"]
        for t in production_tools:
            assert t in tools
    
    def test_ci_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        ci_tools = ["lich_ci_all", "lich_ci_backend", "lich_ci_web", "lich_ci_admin"]
        for t in ci_tools:
            assert t in tools
    
    def test_middleware_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        mw_tools = ["lich_middleware_list", "lich_middleware_enable", "lich_middleware_disable"]
        for t in mw_tools:
            assert t in tools
    
    def test_dev_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        dev_tools = ["lich_dev_start", "lich_dev_stop"]
        for t in dev_tools:
            assert t in tools
    
    def test_utility_tools_exist(self):
        tools = [t.name for t in mcp._tool_manager.list_tools()]
        utility_tools = ["lich_adopt", "lich_upgrade", "lich_version"]
        for t in utility_tools:
            assert t in tools


if __name__ == "__main__":
    test_all_mcp_tools_registered()
    print(f"\n✅ All {EXPECTED_TOOL_COUNT} MCP Tools Verified!")
