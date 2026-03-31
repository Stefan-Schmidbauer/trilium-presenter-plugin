## Images & Size Classes

Control image size with CSS classes:

::: {.columns}
::: {.column}
### Available Sizes

| Class | Height | Use Case |
|-------|--------|----------|
| `.img-tiny` | 64px | Icons |
| `.img-small` | 128px | Logos |
| `.img-medium` | 192px | Diagrams |
| `.img-large` | 384px | Charts |
| `.img-xlarge` | 480px | Full-size |

Add `.center` to center horizontally.
:::
::: {.column}
### Syntax

```markdown
![Alt text](file.png){.img-medium .center}
```

Images are attached to the slide note and referenced by filename — the plugin resolves the URL automatically.

Without classes, images display at natural size (max-width: 100%).
:::
:::

::: {.notes}
- Point out that attachment filenames must match exactly
- Show how to attach an image to a note in Trilium
- Demonstrate different size classes if time permits
:::
