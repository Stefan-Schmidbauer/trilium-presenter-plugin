# MCP Server (AI Slide Authoring)

Trilium Presenter ships with an optional **MCP server** that lets an AI assistant (e.g. Claude) create and manage presentations for you — directly in Trilium, via the ETAPI.

## What it can do

- Create presentations and slides from a prompt
- Update, reorder, clone, and delete slides
- Build a **Master / Sets** slide library — reuse one slide across many presentations

The assistant follows the slide format you define in Trilium: the compact **Slide Format** note (label `#presenterSlideFormat`) is embedded live into the `create_slide` / `update_slide` tool descriptions, so it reliably reaches the AI regardless of the client — one source of truth for humans and AI alike. The longer **Slide Content** note stays as the full syntax reference. (Format changes take effect on the AI's next connection.)

## Setup

The server lives in the `mcp/` folder of the plugin repository. Full setup — Python, configuration, and Claude Desktop — is documented on GitHub:

→ **[mcp/README.md](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin/tree/main/mcp)**
