from mcp.server.fastmcp import FastMCP
from lich.mcp.tools import (
    project, make, git, qa, ops,
    routes, seed, migration, secret, production, ci, mw, dev, utility
)

# Initialize FastMCP Server
mcp = FastMCP("Lich Framework")

# Register all tool groups
# Core project tools
project.register_project_tools(mcp)

# Code generation tools
make.register_make_tools(mcp)

# Git workflow tools
git.register_git_tools(mcp)

# QA tools (lint, test, security)
qa.register_qa_tools(mcp)

# Ops tools (deploy, backup)
ops.register_ops_tools(mcp)

# Routes (list API endpoints)
routes.register_routes_tools(mcp)

# Database seeding
seed.register_seed_tools(mcp)

# Database migrations (Alembic)
migration.register_migration_tools(mcp)

# Secret management
secret.register_secret_tools(mcp)

# Production readiness checks
production.register_production_tools(mcp)

# CI checks
ci.register_ci_tools(mcp)

# Middleware management
mw.register_middleware_tools(mcp)

# Development environment
dev.register_dev_tools(mcp)

# Utility tools (adopt, upgrade, version)
utility.register_utility_tools(mcp)


def start_server():
    """Start the MCP server on stdio."""
    print("🤖 Lich MCP Server Starting...", flush=True)
    mcp.run()
