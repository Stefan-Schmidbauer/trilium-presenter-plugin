# Slide Format

One slide = one Trilium child note, type Code / Markdown (`text/x-markdown`).
Pandoc-compatible Markdown.

## Structure (required)
- Exactly one H1 per slide: `# Title`. Emoji prefix optional (`# 🎯 Title`).
- Short bullets, one line each. Split dense content across multiple slides.
- Code blocks ≤ ~10 lines.
- Never use `---` (each slide is its own note; `---` is reserved).
- Pair `❌` (anti-pattern) with `✅` (recommended) where it clarifies.
- Speaker notes go in a trailing block: `::: {.notes}` … `:::`

## Layout building blocks
- Columns (auto-detected, up to 4):
  `::: {.columns}` → per column `::: {.column}` … `:::` → close `:::`
- Images: `![alt](api/images/<noteId>/<file>){.img-medium .center}`
  Sizes: `.img-tiny` / `.img-small` / `.img-medium` / `.img-large` /
  `.img-xlarge` / `.img-fill` / `.img-fit` · `.center` to center.
- Tables: `| Col | Col |` header + required `|---|---|` separator row.
  Inline bold/italic/code/links work in cells.
- PDF page break: `::: {.page-break}` … `:::`

## Conventions & Voice
Language, address form (formal/informal) and tone are NOT fixed by the plugin.

⛔ MANDATORY: If `Conventions` below is `<unset>`, you MUST STOP and ask
the author for language, address form and tone BEFORE writing ANY slide
content. Do NOT proceed until the author has answered. No exceptions.

Once the author has answered: apply the conventions consistently and offer to
pin them here. If `Conventions` is already set: follow them, do not ask.

Conventions: <unset>
<!-- Example once pinned: Language: German · Address: formal (Sie) · Tone: direct, practical. -->

## Full reference
Long examples & all options: see the **Slide Content** reference note (human-facing).
