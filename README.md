# Trilium Presenter Plugin

Turn any Trilium note into a fullscreen presentation -- directly from Trilium, with one click.

## Features

- **One-click presentations** from any note with children
- **Markdown slides** with Pandoc-compatible syntax (columns, speaker notes, code blocks)
- **Depth-first traversal** -- organize slides in sub-topics, they unfold automatically
- **Presenter mode** with speaker notes and slide list, synced via BroadcastChannel
- **Handout/PDF export** with one page per slide
- **Theme system** -- CSS + SVG backgrounds as Trilium notes, selectable per presentation
- **Slide templates** -- 11 ready-made layouts for quick slide creation
- **Keyboard, mouse & touch navigation** with progress bar
- **Configurable language** via `#presenterLang` label

## Installation

1. Download `trilium-presenter-plugin.zip` from the [latest release](../../releases/latest)
2. In Trilium, right-click any note in the tree and select **Import into note**
3. Select the downloaded `.zip` file
4. Trilium disables imported widgets by default -- open the **Widget** note inside the imported "Trilium Presenter" tree, find the `#disabled:widget` attribute and rename it to `#widget`
5. Reload Trilium (Ctrl+R) -- the **Trilium Presenter** widget appears in the right panel

## Quick Start

**Fastest way:** Navigate to the imported **Example Presentation** note and click **Present** -- it walks you through all features including Markdown syntax, columns, images, and the Master/Clone workflow.

**From scratch:**

1. Create a note and add child notes -- each child becomes a slide
2. Set child note type to **Code** with language **Markdown** (`text/x-markdown`)
3. Navigate to your presentation note and click **Present** in the right panel

## Slide Organization

Slides are collected via **depth-first pre-order traversal**:

```
My Presentation
  Title Slide              -> Slide 1
  Introduction             -> Slide 2
  Deep Dive                -> Slide 3 (section break)
    Details A              -> Slide 4
    Details B              -> Slide 5
  Conclusion               -> Slide 6
```

Container notes (`text/html` type) are skipped but their children are included. This lets you use folders to organize slides without creating empty slides.

## Modes

| Button | Description |
|--------|-------------|
| **Present** | Fullscreen presentation in a new window |
| **Presenter Mode** | Speaker view with notes, slide list, and BroadcastChannel sync |
| **Handout (PDF)** | Print-optimized view, one page per slide, auto-opens print dialog |

## Themes

Select a theme from the dropdown before presenting. Themes are Trilium notes with the `#presenterTheme` label containing CSS sub-notes (Base, Title Slide, Content Slide) and optional SVG background attachments.

Included themes: **Default** (light) and **Dark**.

## Slide Types

The first slide defaults to `title` layout, others to `content`. Override with `#slideType` label:
- `#slideType=title` -- Title slide styling
- `#slideType=content` -- Content slide styling
- Custom types by adding matching CSS notes to your theme

## Configuration

| Label | Description | Default |
|-------|-------------|---------|
| `#presenterLang` | HTML lang attribute | `en` |
| `#slideType` | Slide layout type | auto |
| `#presenterTheme` | Mark a note as theme | -- |

## Documentation

See the [docs/](docs/) folder:
- [Getting Started](docs/getting-started.md)
- [Slide Content](docs/slide-content.md) -- full Markdown & Pandoc syntax reference
- [Themes](docs/themes.md) -- creating custom themes
- [Content Organization](docs/content-organization.md) -- clone-based slide library workflow

## Author

**Stefan Schmidbauer** -- [GitHub](https://github.com/Stefan-Schmidbauer)

Built with [Claude Code](https://claude.ai/claude-code) as co-author.

## License

MIT -- see [LICENSE](LICENSE)
