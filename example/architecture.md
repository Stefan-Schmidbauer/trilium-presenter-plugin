## Plugin Architecture

::: {.columns}
::: {.column}
### Data Collection

- `api.runOnBackend()`
- Depth-first traversal
- Content & attachment fetching
- Theme CSS loading
:::
::: {.column}
### Rendering Engine

- Markdown → HTML
- Pandoc div processing
- Image URL resolution
- SPA assembly
:::
::: {.column}
### Presentation

- Widget (right panel)
- Keyboard & click navigation
- Presenter mode + notes
- BroadcastChannel sync
:::
:::

::: {.notes}
Single widget note handles everything — backend call collects data,
then the rendering engine and presentation layer run client-side.
:::
