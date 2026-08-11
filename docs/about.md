# About

**Trilium Presenter** turns a Trilium note and its children into a fullscreen
presentation, with themes, templates and a presenter view.

It is the presentation specialist of the **Notecast** family — three tools that
read and write the same Trilium notes, each doing exactly one job:

| Repo | Role |
|---|---|
| [trilium-presenter-plugin](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin) | **Presenting** — renders a subtree as an on-screen slide deck |
| [trilium-notecast-mcp](https://github.com/Stefan-Schmidbauer/trilium-notecast-mcp) | **Authoring** — an AI assistant writes typed notes via the ETAPI |
| [trilium-notecast-render](https://github.com/Stefan-Schmidbauer/trilium-notecast-render) | **Rendering** — renders a note to print/PDF in a chosen theme |

They never call each other, and each is installed separately. The only thing
they share is a set of Trilium labels under the `notecast` prefix — that is the
entire contract, and keeping it thin is the point.

`notecast` is a label namespace and a family name, not a naming rule for repos:
this plugin predates it, keeps its established name, and keeps its own
`#presenterTheme` and `#slideIgnore` labels outside the shared namespace.

**Printing is the renderer's job.** This plugin presents; to put a deck on
paper, install trilium-notecast-render alongside it and tick *Include subtree*.

## Author

**Stefan Schmidbauer** — [GitHub](https://github.com/Stefan-Schmidbauer)

Built with [Claude](https://claude.ai) as AI co-author.

## Source Code

[github.com/Stefan-Schmidbauer/trilium-presenter-plugin](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin)

- [Releases](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin/releases)
- [Issues & Feedback](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin/issues)

## License

MIT — see [LICENSE](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin/blob/main/LICENSE) for details.
