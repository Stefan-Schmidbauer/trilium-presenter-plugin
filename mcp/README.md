# trilium-mcp

MCP server for [Trilium Notes](https://github.com/TriliumNext/Trilium) — create and manage [Trilium Presenter](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin) slide presentations via the ETAPI.

This server lives in the `mcp/` folder of the **trilium-presenter-plugin** repository. The slide format it follows is loaded live from the Trilium note labelled `#presenterSlideFormat` (the compact **Slide Format** note) and embedded directly into the `create_slide` / `update_slide` tool descriptions, so it reliably reaches the model on every client. Format and conventions stay in a single place — editable directly in Trilium. Changes take effect on the next connection; if the note is missing, a built-in fallback keeps the tools working.

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
| `slide_creation_guide` | Full slide guide + conventions, loaded live from the Trilium note labelled `#presenterSlideFormat` (falls back to a built-in guide). Note: the same format is also embedded into the `create_slide` / `update_slide` tool descriptions, which is the path guaranteed to reach the model — prompts are not injected by every client. |

## Setup

### 1. Prerequisites

- Python 3.11+
- A Trilium ETAPI token: **Trilium → Options → ETAPI → Create new token**

### 2. Install

The server ships inside the [trilium-presenter-plugin](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin) repository:

```bash
git clone https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin
cd trilium-presenter-plugin/mcp
python3 -m venv .venv
.venv/bin/pip install mcp httpx
```

### 3. Configure

```bash
cp claude_desktop_config.example.json claude_desktop_config.json
```

Edit `claude_desktop_config.json` — fill in your values:

| Key | Description |
|---|---|
| `TRILIUM_URL` | Local URL of Trilium (default: `http://localhost:9160`) |
| `TRILIUM_API_KEY` | Your ETAPI token |
| `TRILIUM_DEFAULT_PARENT` | Note ID where new presentations are created (default: `root`) |

### 4. Add to Claude Desktop

Copy the `mcpServers` block from your `claude_desktop_config.json` into:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### 5. Local development (without Claude Desktop)

```bash
python dev.py
```

Reads config directly from `claude_desktop_config.json` and starts the server.

## Content Organization

The server supports the **Master / Sets** workflow from Trilium Presenter:

- **Master** — central slide library organized by topic
- **Sets** — finished presentations assembled from Master slides via `clone_slide`
- Cloned slides share a single source: edit once, update everywhere
