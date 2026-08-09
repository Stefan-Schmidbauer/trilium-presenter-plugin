# Getting Started

Trilium Presenter turns any note into a fullscreen presentation — directly from Trilium, with one click.

## Install

Import the plugin's `.zip` into Trilium (**Note tree → … → Import into note**), then **enable the widget**: Trilium neutralises executable labels in anything you import, so the **Widget** note arrives carrying `#disabled:widget` instead of `#widget`. Until you rename it back, the plugin is installed but inert and no widget appears.

1. Open the **Widget** note inside the imported *Trilium Presenter* tree and switch to its *Owned attributes*.
2. Rename `#disabled:widget` to `#widget` and save.
3. Reload Trilium (Ctrl+R) — widgets are only read at startup.

## How It Works

1. **Create a note** — this is your presentation
2. **Add child notes** — each child becomes a slide
3. **Write content in Markdown** (note type: Code, language: Markdown)
4. **Navigate to your presentation note** in Trilium
5. **Click ▶ Present** in the right panel

That's it. No export, no conversion, no external tools.

## Creating Your First Presentation

### Step 1: Create the Presentation Note

Create a new note anywhere in your Trilium tree. This note is the container — its title becomes the presentation title, and its children become the slides.

### Step 2: Add Slides

Add child notes to your presentation. Each child note is one slide.

**Important:** Set the note type to **Code** and the language to **Markdown** (`text/x-markdown`). This gives you clean Markdown editing without Trilium's WYSIWYG editor interfering with the Pandoc syntax.

### Step 3: Write Content

Write your slide content in Markdown. See the **Slide Content** documentation for the full syntax reference including multi-column layouts, speaker notes, and image handling.

### Step 4: Present

Navigate to your presentation note. In the right panel, you'll see:

- **▶ Present** — Opens a fullscreen presentation in a new browser window
- **🖥 Presenter Mode** — Opens a speaker view with notes and slide list

### Single Slide Preview

When viewing an individual Markdown code note (without children), the widget shows a **🔎 Show Slide** button with theme selection. This lets you preview any single slide as a themed presentation — useful for checking how a slide looks before assembling a full presentation.

### Slide Order

Slides appear in the order shown in Trilium's tree. Drag and drop child notes to reorder your slides.

### Slide Types

By default, the **first slide** gets the title layout, all others get the content layout. Override this by adding a `#slideType` label to individual notes:

- `#slideType=title` — Title slide styling and background
- `#slideType=content` — Content slide styling and background

You can also create **custom slide types** (e.g., `#slideType=chapter`) by adding a matching CSS note to your theme. See the **Themes** documentation for details.

### Themes

Select a theme from the **Theme** dropdown in the widget before starting your presentation. See the **Themes** documentation for details on creating custom themes.

## Configuration

### Language

The HTML `lang` attribute of the generated presentation defaults to `en`. To change it, add a `#presenterLang` label to your presentation note:

- `#presenterLang=de` — German
- `#presenterLang=fr` — French
- etc.

This affects the presentation and presenter mode.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| → ↓ Space PageDown | Next slide |
| ← ↑ Backspace PageUp | Previous slide |
| Home | First slide |
| End | Last slide |
| Escape | Toggle fullscreen |
| h or ? | Show keyboard hint |

**Mouse:** Click the right half of the screen for next, left half for previous.

## Presenter Mode

The presenter view shows:
- **Current slide title** and slide number
- **Speaker notes** (from `::: {.notes}` blocks in your Markdown) — rendered as full Markdown with formatting support
- **Clickable slide list** for jumping to any slide

The presenter window stays synchronized with the main presentation via BroadcastChannel — navigating in one window updates the other.

## Handouts and PDF

This plugin no longer prints. Handouts are made by the sibling plugin
[trilium-notecast-render](https://github.com/Stefan-Schmidbauer/trilium-notecast-render):
open the presentation note, tick **Include subtree** in its render widget, and
print — you get one page per slide, in tree order.

The move gained more than it cost. The renderer prints *any* Notecast type the
same way, so the deck, the meeting notes and the checklists all take one path;
its slide theme is landscape, which the presenter's portrait handout never was;
and this plugin is now only responsible for what happens on screen.

One difference to expect if you printed handouts before v2: the renderer reads
none of this plugin's labels, so **`#slideIgnore` does not exclude anything from
a printout**. A branch you keep off screen with it is still printed — see
*Excluding Notes from a Presentation* in Content Organization.

## Images

Two ways to include images:

**Attachment** (recommended): Upload an image as an attachment to the slide note, then reference it by filename:
```markdown
![Description](filename.png){.img-medium .center}
```
The plugin automatically resolves attachment filenames to the correct API URLs.

**Direct API URL**: Reference an attachment or image note directly:
```markdown
![Description](api/attachments/ATTACHMENT_ID/image/filename.png){.img-medium .center}
```


## Slide Templates

The plugin includes ready-made templates for common slide layouts:

| Template | Description |
|----------|-------------|
| **Title** | Title, subtitle, and author |
| **Agenda** | Numbered agenda list |
| **Bullet Points** | Heading with bullet list |
| **Two Columns** | Side-by-side comparison |
| **Three Columns** | Three-column overview |
| **Image** | Large centered image |
| **Image with Text** | Text left, image right |
| **Code** | Code block with explanation |
| **Quote** | Blockquote with attribution |
| **Chapter** | Chapter divider (title style) |
| **Thank You** | Closing slide with contact info |

To use a template: Right-click your presentation note, select **Insert child note**, and choose from the template list. Each template includes sample speaker notes.

## What's Skipped

Child notes of type `image` or `file` are automatically skipped — they won't become slides. This means you can import images into your presentation note without them appearing as slides.
