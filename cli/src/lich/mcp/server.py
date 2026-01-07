from mcp.server.fastmcp import FastMCP
from lich.mcp.tools import project, make, git, qa, ops

# Initialize FastMCP Server
mcp = FastMCP("Lich Framework")

# Register all tool groups
project.register_project_tools(mcp)
make.register_make_tools(mcp)
git.register_git_tools(mcp)
qa.register_qa_tools(mcp)
ops.register_ops_tools(mcp)

def start_server():
    """Start the MCP server on stdio."""
    print("🤖 Lich MCP Server Starting...", flush=True)
    mcp.run()
