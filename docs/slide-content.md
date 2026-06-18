# Slide Content

Trilium Presenter uses **Pandoc-compatible Markdown** for slide content. This reference covers all supported syntax.

## Slide Style

A few conventions keep slides consistent and presentation-ready:

- **One H1 per slide** — start each slide with a level-1 heading (`# Title`). An emoji prefix is optional (`# 🎯 Title`).
- **Short bullets** — one line each; split dense points across multiple slides.
- **No `---`** — see *Horizontal Rules* below.
- **Contrast for clarity** — pair `❌` (anti-pattern) with `✅` (recommended) where it helps.
- **Short code blocks** — keep code to ~10 lines so it stays readable on screen.

## Conventions & Voice

Language, address form (formal vs. informal), and tone are **not fixed** by the plugin — they depend on you and your audience.

> **No conventions defined.** When creating slides, ask the author for **language**, **address form** (formal / informal), and **tone**, then apply them consistently. Offer to record the answers in this section so they become the single source for future slides.

Replace the quote above with your own conventions to pin them, for example:

> Language: German · Address: formal ("Sie") · Tone: direct, practical.

## Basic Formatting

```markdown
# Heading 1
## Heading 2
### Heading 3

Regular paragraph text.

**Bold text** and *italic text* and ***bold italic***.

`inline code`
```

## Lists

```markdown
- Unordered item
- Another item
- Third item

1. Ordered item
2. Second item
3. Third item
```

## Links

```markdown
[Link text](https://example.com)
```

## Blockquotes

```markdown
> This is a quote.
> It can span multiple lines.
```

## Horizontal Rules — Do Not Use

Do **not** use `---` in slides. Each slide is its own Trilium note, so there is
no need for an in-slide separator — and `---` is reserved/avoided to prevent
confusion with slide boundaries.

## Code Blocks

````markdown
```python
def hello():
    print("Hello, World!")
```

```javascript
const greet = () => console.log("Hello!");
```
````

## Multi-Column Layouts

Create side-by-side content using Pandoc fenced divs:

### Two Columns

```markdown
::: {.columns}
::: {.column}
Left column content
:::
::: {.column}
Right column content
:::
:::
```

### Three Columns

```markdown
::: {.columns}
::: {.column}
Column 1
:::
::: {.column}
Column 2
:::
::: {.column}
Column 3
:::
:::
```

The number of columns is detected automatically. Up to 4 columns are supported.

## Speaker Notes

Add notes visible only in Presenter Mode:

```markdown
# My Slide

Visible content here.

::: {.notes}
- Remember to mention X
- Show demo next
- Time budget: 5 minutes
:::
```

Speaker notes support Markdown formatting and appear in the Presenter Mode window, but not in the presentation itself.

## Images

### With CSS Size Classes

```markdown
![Description](file.svg){.img-medium .center}
```

**Available size classes:**

| Class | Height | Use Case |
|-------|--------|----------|
| `.img-tiny` | 64px (4rem) | Icons, small logos |
| `.img-small` | 128px (8rem) | Small graphics |
| `.img-medium` | 192px (12rem) | Diagrams |
| `.img-large` | 384px (24rem) | Large diagrams |
| `.img-xlarge` | 480px (30rem) | Full-height graphics |
| `.img-fill` | 100% | Fill entire area |
| `.img-fit` | auto | Responsive fit |

**Positioning:** Add `.center` to center the image horizontally.

### Without Classes

```markdown
![Description](filename.png)
```

Images without classes display at their natural size, constrained to max-width: 100%.

## Page Breaks (PDF)

```markdown
::: {.page-break}
:::
```

## Tables

```markdown
| Feature | Status |
|---------|--------|
| Columns | Done |
| Tables  | Done |
```

The first row becomes the table header, the separator row (`|---|---|`) is required. Inline formatting (bold, italic, code, links) works inside table cells.

## Complete Slide Example

```markdown
# Project Architecture

::: {.columns}
::: {.column}
### Frontend
- React + TypeScript
- Tailwind CSS
- Vite build
:::
::: {.column}
### Backend
- Python + FastAPI
- PostgreSQL
- Redis cache
:::
:::

![Architecture Diagram](arch.svg){.img-large .center}

::: {.notes}
Walk through each component. Emphasize the API layer.
Duration: 5 minutes.
:::
```
