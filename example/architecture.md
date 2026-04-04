## Columns & Speaker Notes

### Multi-Column Layouts

Wrap content in Pandoc fenced divs:

```markdown
::: {.columns}
::: {.column}
Left side
:::
::: {.column}
Right side
:::
:::
```

Up to **4 columns** are supported — the layout adjusts automatically.

### Speaker Notes

Add notes that only appear in Presenter Mode:

```markdown
::: {.notes}
Only visible in Presenter Mode — not on the slide itself.
:::
```

::: {.notes}
This text is a speaker note — it only shows in Presenter Mode, not on the projected slide.
:::