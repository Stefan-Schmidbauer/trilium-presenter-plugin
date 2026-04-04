## Images in Slides

Attach an image to your slide note, then reference it by filename:

```markdown
![Workflow](workflow.svg){.img-large .center}
```

![Workflow](workflow.svg){.img-large .center}

| Class | Height | Use Case |
|-------|--------|----------|
| `.img-small` | 128px | Logos |
| `.img-medium` | 192px | Diagrams |
| `.img-large` | 384px | Charts |
| `.img-xlarge` | 480px | Full-size |

::: {.notes}
The image above is an SVG attachment on this slide note. The plugin resolves filenames to Trilium API URLs automatically. Add `.center` to center horizontally.
:::