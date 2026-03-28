# Content Organization

Instead of creating presentations from scratch each time, build a **library of reusable slides** and assemble different presentations by cloning them. This guide explains a professional workflow using Trilium's cloning feature.

**Key Concept**: Separate your content library (Master) from your finished presentations (Sets). Use Trilium's **clone feature** to reuse slides across multiple presentations while maintaining a single source of truth.

## The Structure

```
Presentations
  Master        (Your content library)
  Sets          (Finished presentations)
  Templates     (Reusable layouts - optional)
```

## Master - Your Slide Library

The **Master** area is your central repository where all original slides live, organized by topics.

```
Master
  Topic A
    Slide - Introduction to A
    Slide - A Deep Dive
  Topic B
    Slide - B Overview
    Slide - B Details
  Topic C
    Slide - C Basics
    Slide - C Advanced
    Slide - C Summary
```

**Purpose**:

- Single source of truth — edit once, update everywhere
- Organized by themes or topics, not by presentation
- The clone symbol in Trilium indicates a cloned note

**Slide format**: Each slide should be a **Code note** with language **Markdown** (`text/x-markdown`). See the **Slide Content** documentation for the full syntax reference.

## Sets - Finished Presentations

The **Sets** area contains your actual presentations, assembled from Master slides using clones.

```
Sets
  Workshop Beginners
    Title                (unique - created from template)
    Agenda               (unique - created from template)
    Introduction to A    (cloned from Master)
    A Deep Dive          (cloned from Master)
    B Overview           (cloned from Master)
    C Basics             (cloned from Master)
    Contact              (cloned or unique)
  Workshop Advanced
    Title                (unique)
    Agenda               (unique)
    A Deep Dive          (cloned from Master)
    B Details            (cloned from Master)
    C Advanced           (cloned from Master)
    C Summary            (cloned from Master)
    Contact              (cloned or unique)
```

Each Set is a presentation note with child slides — exactly the structure Trilium Presenter expects. Select a Set, choose your theme in the widget, and click Present.

## Understanding Clones

Trilium's **clone feature** creates references, not copies:

- **Cloned note**: Shares content with the original. Editing either one updates all instances.
- **Unique note**: Exists only in this presentation (like Title, Agenda).

**When you edit a cloned note**: The change appears in ALL clones and in the Master. Fix a typo once, it updates in every presentation that uses that slide.

**The presenter works the same either way** — Trilium Presenter simply reads the content of each child note. It doesn't care whether a note is a clone or not.

## Templates (Optional)

Templates are slides that appear in most presentations but need unique content each time:

```
Templates
  Title
  Agenda
  Contact
```

**How to use**: Right-click your Set, choose **Insert child note**, and select a template. This creates a new unique note (not a clone) that you can customize for this specific presentation.

## Step-by-Step: Creating a Presentation

### Step 1: Build Your Master Library

1. Create topic folders under Master
2. Create slides within each topic (type: Code, language: Markdown)
3. Use `#slideType=title` or `#slideType=content` labels as needed

**Naming tip**: Use descriptive names like "Slide - Python Variables" rather than just "Variables". The note title doesn't appear on the slide itself — it's only for organization in Trilium and the Presenter Mode slide list.

### Step 2: Create a New Set

1. Create a new note under Sets (e.g., "Workshop Beginners")
2. This note is your presentation container

### Step 3: Clone Slides from Master

1. Navigate to a slide in Master
2. **Right-click** the note title and select **Clone to...**, then select your Set
3. Or **drag and drop** with Ctrl held to clone
4. Repeat for all slides you need
5. Reorder slides by dragging them within your Set

### Step 4: Add Unique Slides

Create presentation-specific content (Title, Agenda) using Templates or by creating new notes directly in your Set.

### Step 5: Present

1. Navigate to your Set in Trilium
2. Select a **Theme** from the dropdown in the right panel
3. Click **Present** — done!

## Clone vs. Unique: When to Use Each

### Use Clone When:

- Content is **shared** across multiple presentations
- You want **automatic updates** when editing the original
- Examples: Topic slides from Master, standard contact slides

### Use Unique When:

- Content is **specific** to one presentation
- Each presentation needs **different content**
- Examples: Title slides, agenda slides

## Best Practices

### Edit in Master, Not in Sets

Always edit content in the Master area. Since clones update automatically, editing in Master updates all presentations that use that slide. Only edit unique slides (Title, Agenda) directly in their Set.

### Organize Master by Topic, Not by Presentation

Use topic folders like "Basics", "Intermediate", "Advanced" rather than "Beginner Workshop Slides". This allows mixing and matching slides for different audiences.

### Make Sets Self-Contained

Each Set should include all slides needed for the presentation — cloned from Master plus unique presentation-specific slides.