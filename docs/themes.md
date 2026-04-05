# Themes

Trilium Presenter uses a simple theme system: each theme is a folder containing CSS notes and optional background images.

## Selecting a Theme

In the Trilium Presenter widget (right panel), you'll see a **Theme** dropdown above the action buttons. Simply select your desired theme before clicking Present.

The dropdown lists all notes in your Trilium tree that have the `#presenterTheme` label. The selection defaults to the theme named **Default** but can be changed at any time.

Themes can live **anywhere** in your Trilium tree — they don't need to be inside the plugin folder. Just add the `#presenterTheme` label to a theme folder and it will appear in the dropdown.

## Theme Structure

A theme folder contains these notes:

```
My Theme
  Base              (CSS code note — shared styles)
  Title Slide       (CSS code note + background.svg attachment)
  Content Slide     (CSS code note + background.svg attachment)
  Handout           (CSS code note — optional, for PDF handout styling)
```

- **Base** — Layout, image sizing, navigation, centering utilities
- **Title Slide** — Typography and styling for title slides, plus a background SVG as attachment
- **Content Slide** — Typography and styling for content slides, columns, code blocks, tables, plus a background SVG as attachment
- **Handout** (optional) — CSS for the print/PDF handout. If omitted, the plugin uses a built-in default handout style

## Included Themes

| Theme | Description |
|-------|-------------|
| **Default** | Clean light theme with blue accents |
| **Dark** | Dark background with red accents, light text |

## Creating a Custom Theme

1. **Create a new folder** anywhere in your Trilium tree (e.g., "My Corporate Theme")
2. **Add the label** `#presenterTheme` to the folder — this is how the plugin discovers themes
3. **Add child notes** (type: Code, language: CSS):
   - `Base` — Copy from an existing theme and modify
   - `Title Slide` — Title-specific styles
   - `Content Slide` — Content-specific styles
4. **Attach backgrounds** — Upload SVG files as attachments named `background.svg` to the Title Slide and Content Slide notes
5. **Select the theme** — Your new theme will automatically appear in the widget dropdown

### Tips

- Start by duplicating an existing theme folder, then modify
- Background SVGs should be **1920x1080** (16:9 Full HD) for optimal display
- CSS uses `.title-slide` and `.content-slide` class selectors
- Test with the Example Presentation to verify your changes

## Custom Slide Types

You can create additional slide types beyond title and content:

1. Add a new CSS note to your theme folder (e.g., "Chapter Slide")
2. The note title determines the CSS class: "Chapter Slide" becomes `.chapter-slide`
3. Attach a `background.svg` if desired
4. Label your slides with `#slideType=chapter`

This allows unlimited slide types: chapter breaks, section dividers, quote slides, image-only slides, etc.

## CSS Reference

The theme CSS uses these selectors:

| Selector | Applies to |
|----------|-----------|
| `html, body` | Global styles |
| `.slide-container` | Full-viewport slide wrapper |
| `.slide-content` | Content area with padding |
| `.title-slide .slide-content` | Title slide layout |
| `.content-slide .slide-content` | Content slide layout |
| `.title-slide h1, h2, h3` | Title slide headings |
| `.content-slide h1, h2, h3` | Content slide headings |
| `.content-slide .columns` | Multi-column grid container |
| `.content-slide .columns-2` | Two-column grid |
| `.content-slide .columns-3` | Three-column grid |
| `.content-slide pre` | Code blocks |
| `.content-slide blockquote` | Blockquotes |
| `.progress-bar` | Bottom progress indicator |
| `.nav-hint` | Keyboard hint overlay |
| `img.img-tiny` through `img.img-xlarge` | Image sizing classes |