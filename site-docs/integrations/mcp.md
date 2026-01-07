# Lich MCP Integration

Lich Framework acts as a **Model Context Protocol (MCP)** server, allowing AI assistants like **Claude Desktop** and **Gemini CLI** to directly interact with your project tools.

## Why use this?
Instead of copying code back and forth, you give the AI "hands" to:
*   [x] Create projects (`lich init`)
*   [x] Generate code (`lich make service`)
*   [x] Check project health (`lich check`)

## 1. Setup for Claude Desktop 🤖

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lich": {
      "command": "python3",
      "args": [
        "-m",
        "lich",
        "serve"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/lich/cli/src"
      }
    }
  }
}
```
*(Note: Replace `/path/to/your/lich...` with the actual path if not globally installed)*

## 2. Setup for Generic MCP Clients 🔌

Run the server manually to test connection:

```bash
lich serve
```

This starts the server on **Standard Input/Output (stdio)** using JSON-RPC.

## 3. Available Tools

| Tool Name | Description |
| :--- | :--- |
| `lich_init` | Initialize a new project from template. |
| `lich_make_service` | Create a new Backend Service Domain. |
| `lich_make_entity` | Create a new Database Entity. |
| `lich_check_project` | Verify if current directory is valid. |

## 4. Example Usage
**User**: "Claude, please create a new service called `orders` and an entity called `Order`."
**Claude**: *Calls `lich_make_service("orders")` and `lich_make_entity("Order")` automatically.*
**Result**: Files are created instantly on your disk.
