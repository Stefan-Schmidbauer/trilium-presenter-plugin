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
- Images: `![alt](filename.png){.img-medium .center}` — a **bare file name**, no
  path and no URL. The image is an attachment of this slide's own note, and the
  name is matched against the attachment titles. `attach_image` returns exactly
  this form; never construct a URL by hand.
  Sizes: `.img-tiny` / `.img-small` / `.img-medium` / `.img-large` /
  `.img-xlarge` / `.img-fill` / `.img-fit` · `.center` to center.
- Tables: `| Col | Col |` header + required `|---|---|` separator row.
  Inline bold/italic/code/links work in cells.
- Page break for print: `::: {.page-break}` … `:::` — read by
  trilium-notecast-render, which does the printing.

## Conventions & Voice
Write in **German** unless the author has asked for another language. Follow that
request for the whole set of slides, not just the one being written.

Address form and tone are NOT fixed by the plugin. A slide deck speaks to an
audience directly, so the address form is visible on the first slide already.

⛔ MANDATORY: If `Conventions` below is `<unset>`, you MUST STOP and ask the
author for address form and tone BEFORE writing ANY slide content. Do NOT
proceed until the author has answered. No exceptions.

Once the author has answered: apply the conventions consistently and offer to
pin them here. If `Conventions` is already set: follow them, do not ask.

Conventions: Language: German · Address: formal (Sie) · Tone: direct, practical.

## Full reference
Long examples & all options: see the **Slide Content** reference note (human-facing).
