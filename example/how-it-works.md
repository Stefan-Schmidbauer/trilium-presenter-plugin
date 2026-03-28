## How It Works

The widget reads your note tree via `api.runOnBackend()`:

```javascript
function collectSlides(note, visited) {
    if (visited.has(note.noteId)) return;
    visited.add(note.noteId);

    slides.push({
        title: note.title,
        content: note.getContent(),
        type: note.getLabelValue('slideType')
    });

    for (const child of getSortedChildren(note)) {
        collectSlides(child, visited);
    }
}
```

Depth-first traversal — no export, no conversion, **direct rendering**.

::: {.notes}
- Explain depth-first: parent slide first, then children, then next sibling
- Mention that text/html container notes are skipped (only code/markdown becomes slides)
- Demo: show the Trilium tree while presenting
:::
