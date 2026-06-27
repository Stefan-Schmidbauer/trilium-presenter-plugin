# trilium-mcp

MCP server for [Trilium Notes](https://github.com/TriliumNext/Trilium) — create and manage [Trilium Presenter](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin) slide presentations via the ETAPI.

This server lives in the `mcp/` folder of the **trilium-presenter-plugin** repository. The slide format it follows is loaded live from the Trilium note labelled `#presenterSlideFormat` (the compact **Slide Format** note) and embedded directly into the `create_slide` / `update_slide` tool descriptions, so it reliably reaches the model on every client. Format and conventions stay in a single place — editable directly in Trilium. Changes take effect on the next connection; if the note is missing or unreachable, the tools emit a loud "format unavailable — do not guess" notice instead of a silent substitute, so a missing format can never masquerade as the real one.

## Tools

| Tool | Description |
|---|---|
| `create_presentation` | Create a new presentation (parent note) |
| `list_presentations` | List presentations under a parent note |
| `get_note_info` | Get note metadata |
| `create_slide` | Create a slide (Markdown code note + `#slideType`) |
| `get_slide` | Read slide Markdown content |
| `update_slide` | Update slide content, title, or type |
| `list_slides` | List all slides in a presentation |
| `delete_note` | Delete a slide or presentation |
| `clone_slide` | Clone a Master slide into a presentation |
| `move_slide` | Reorder slides |
| `search_notes` | Search notes (supports `#label` syntax) |

## Prompts

| Prompt | Description |
|---|---|
| `slide_creation_guide` | Full slide guide + conventions, loaded live from the Trilium note labelled `#presenterSlideFormat` (returns a STOP "do-not-guess" notice if that note is missing or unreachable — never a built-in substitute). Note: the same format is also embedded into the `create_slide` / `update_slide` tool descriptions, which is the path guaranteed to reach the model — prompts are not injected by every client. |

## Setup

### 1. Prerequisites

- Python 3.11+
- A Trilium ETAPI token: **Trilium → Options → ETAPI → Create new token**

### 2. Install

The server ships inside the [trilium-presenter-plugin](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin) repository:

```bash
git clone https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin
cd trilium-presenter-plugin/mcp
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

This creates the `venv/` folder the config below points at.

> **Windows:** use the `venv\Scripts\` paths instead of `venv/bin/` throughout
> this guide — e.g. `venv\Scripts\pip.exe install -r requirements.txt` to
> install and `venv\Scripts\python.exe` as the `command` in the config below.

### 3. Register the server in your MCP client

The server is configured entirely through three environment variables:

| Key | Description |
|---|---|
| `TRILIUM_URL` | Local URL of Trilium (default: `http://localhost:8080`) |
| `TRILIUM_API_KEY` | Your ETAPI token |
| `TRILIUM_DEFAULT_PARENT` | Note ID where new presentations are created (default: `root`) |

Copy the following block into your MCP client config and replace the two
absolute paths and the env values with your own. Use **absolute** paths — MCP
clients do not resolve `~` or relative paths.

```json
{
  "mcpServers": {
    "trilium-presenter": {
      "command": "/path/to/trilium-presenter-plugin/mcp/venv/bin/python",
      "args": ["/path/to/trilium-presenter-plugin/mcp/server.py"],
      "env": {
        "TRILIUM_URL": "http://localhost:8080",
        "TRILIUM_API_KEY": "your-etapi-token",
        "TRILIUM_DEFAULT_PARENT": "root"
      }
    }
  }
}
```

The same block lives in [`claude_desktop_config.example.json`](claude_desktop_config.example.json) — copy it to a real file and fill in your values:

```bash
cp claude_desktop_config.example.json claude_desktop_config.json
```

This `claude_desktop_config.json` is just a scratch file for assembling the `mcpServers` block before you paste it into your client — it is gitignored and not read by the server itself.

Where to paste the `mcpServers` block depends on your client:

- **Claude Code (project-scoped):** `.mcp.json` in your project root
- **Claude Desktop — macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Desktop — Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Claude Desktop — Linux:** `~/.config/Claude/claude_desktop_config.json`

Restart the client after editing its config so the server is picked up.

### 4. Test the server (without an MCP client)

The server speaks MCP over stdio, so running it standalone just blocks waiting
for input. To inspect and exercise the tools interactively, use the
[MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
TRILIUM_URL=http://localhost:8080 TRILIUM_API_KEY=your-etapi-token \
  npx @modelcontextprotocol/inspector venv/bin/python server.py
```

This opens a local UI where you can list and call each tool against your
Trilium instance.

## Content Organization

The server supports the **Master / Sets** workflow from Trilium Presenter:

- **Master** — central slide library organized by topic
- **Sets** — finished presentations assembled from Master slides via `clone_slide`
- Cloned slides share a single source: edit once, update everywhere
