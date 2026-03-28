# Roadmap

## Completed

- [x] One-click presentation from any note with children
- [x] Markdown rendering: headings, lists, bold/italic, code blocks, blockquotes, links, images, horizontal rules
- [x] Pandoc fenced divs: multi-column layouts (2/3/4 columns), speaker notes
- [x] SPA architecture: instant slide transitions, no page reloads
- [x] Keyboard and click navigation with progress bar
- [x] Presenter mode with speaker notes and slide list
- [x] BroadcastChannel sync between presentation and presenter windows
- [x] Theme system: CSS + SVG backgrounds as Trilium notes
- [x] Per-presentation theme selection via `#presenterTheme` label
- [x] Slide type labels (`#slideType`) with custom CSS per type
- [x] Three included themes: Default (light), SSC-KI (corporate), Dark
- [x] Image support via attachments and image note references
- [x] Example presentation included
- [x] Handout (PDF) with page break per slide
- [x] Markdown rendering for speaker notes in presenter mode
- [x] Configurable `lang` attribute via `#presenterLang` label (default: `en`)
- [x] 11 slide templates (Title, Agenda, Bullet Points, Two/Three Columns, Image, Image with Text, Code, Quote, Section Break, Thank You)

## Planned

### Rendering
- [ ] Markdown tables
- [ ] Nested lists (multiple indentation levels)
- [ ] Syntax highlighting for code blocks (highlight.js or Prism)
- [ ] `{.center}` attribute on paragraphs and headings
- [ ] Support for `type=text` (HTML) notes as slides

### Navigation & UX
- [ ] Touch navigation (swipe in bottom screen area)
- [ ] P-key to open presenter from presentation window
- [ ] Slide counter display (optional)
- [ ] Smooth slide transitions (CSS animations)
- [ ] Context menu disabled in presentation

### Presenter Mode
- [ ] Next slide preview
- [ ] Timer / clock

### Configuration
- [ ] Configuration note (JSON) for navigation options and defaults
- [ ] Promoted attributes for easy theme selection in Trilium UI

### Export & Distribution
- [ ] Plugin as .zip export (one-click install for other users)
- [ ] Standalone HTML export (single file, offline presentable)

### Advanced
- [ ] Slide transitions (fade, slide-in)
- [ ] Embedded Mermaid diagrams
- [ ] LaTeX formulas (KaTeX/MathJax)
- [ ] Live reload on note change
