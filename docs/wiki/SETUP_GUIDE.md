# Lich MCP Setup Guide

Configure AI tools to use Lich's 47+ MCP tools in seconds.

## Quick Start

```bash
# Interactive mode (recommended)
lich setup

# Or configure directly
lich setup antigravity   # Google Gemini CLI / Antigravity
lich setup claude        # Claude Desktop
lich setup cursor        # Cursor IDE
lich setup vscode        # VS Code
lich setup all           # All of the above
```

## Check Status

```bash
lich setup status
```

## Supported Tools

| Tool | Scope | Config Location |
|------|-------|-----------------|
| Antigravity | Global | `~/.gemini/settings.json` |
| Claude Desktop | Global | `~/.claude/claude_desktop_config.json` |
| Cursor | Project | `.cursor/mcp.json` |
| VS Code | Project | `.vscode/mcp.json` |

## After Setup

**Restart your AI tool** to activate Lich MCP.

Test by asking: *"What Lich tools are available?"*

## Manual Configuration

If you prefer manual setup, add this to your config:

### Antigravity / Claude
```json
{
  "mcpServers": {
    "lich": {
      "command": "lich",
      "args": ["serve"]
    }
  }
}
```

### VS Code
```json
{
  "servers": {
    "lich": {
      "command": "lich",
      "args": ["serve"],
      "type": "stdio"
    }
  }
}
```

## Troubleshooting

**"lich command not found"**
```bash
pip install lich
```

**MCP not connecting**
1. Check `lich setup status`
2. Restart your AI tool
3. Run `lich serve` manually to test
