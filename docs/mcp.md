# MCP Server (AI Slide Authoring)

An optional **MCP server** lets an AI assistant (e.g. Claude) create and manage slides for you — directly in Trilium, via the ETAPI.

The server is **not part of this plugin**. It is a separate project, [trilium-notecast-mcp](https://github.com/Stefan-Schmidbauer/trilium-notecast-mcp), installed and run independently, then pointed at your Trilium. The two meet only inside Trilium.

## What it can do

- Create slides from a prompt, into any parent note
- Update, reorder, clone, and delete notes
- Build a **Master / Sets** slide library — reuse one slide across many presentations

## How it knows the slide format

The server is a **generic authoring engine**: it ships no formats of its own. What it can write is defined by notes in *your* Trilium, and this plugin supplies the definition for slides.

The **Slide Format** documentation note carries the label `#notecastType=slide`. Its content — the slide rules — is loaded live and embedded into the server's `create_note` / `update_note` tool descriptions, so it reliably reaches the AI regardless of the client. That one note is the single source of truth for slide-creation rules, shared by humans and the AI alike. Its labels also carry the mechanics: slides become Code notes with mime `text/x-markdown`, get `#slideType=content`, and are prefixed `Folie`.

The longer **Slide Content** note stays as the full syntax reference for humans.

Format changes take effect on the AI's next connection. If the label is missing or sits on more than one note, the server refuses to create anything and says so, rather than guessing a format.

## Beyond slides

Because a type is just a tagged note, the same server writes whatever else you define — a knowledge-base entry, an expense report, a meeting note. Tag a note with `#notecastType=<id>`, put the authoring rules in its content, and the AI can write that type too. No code change, no reinstall.

`slide` is simply the type this plugin happens to own.

## Setup

Full setup — Python, Docker, configuration, and MCP clients such as Claude Desktop — is documented on GitHub:

→ **[trilium-notecast-mcp](https://github.com/Stefan-Schmidbauer/trilium-notecast-mcp)**
