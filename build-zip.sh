#!/bin/bash
# Build a Trilium-compatible import zip from repo files
set -euo pipefail

OUTDIR="$(mktemp -d)"
ROOT="$OUTDIR/Trilium Presenter"
VERSION="${1:-dev}"

# Root container
cp assets/container-html/"Trilium Presenter.html" "$OUTDIR/"

# Widget
mkdir -p "$ROOT"
cp src/widget.js "$ROOT/Widget.js"

# Documentation
mkdir -p "$ROOT/Documentation"
cp docs/getting-started.md "$ROOT/Documentation/Getting Started.mkd"
cp docs/slide-content.md "$ROOT/Documentation/Slide Content.mkd"
cp docs/themes.md "$ROOT/Documentation/Themes.mkd"
cp docs/content-organization.md "$ROOT/Documentation/Content Organization.mkd"
cp docs/about.md "$ROOT/Documentation/About.mkd"

# Example Presentation
mkdir -p "$ROOT/Example Presentation/Markdown and Layouts" "$ROOT/Example Presentation/Reusable Slides"
cp example/title-slide.md "$ROOT/Example Presentation/Title Slide.mkd"
cp example/what-is-trilium-presenter.md "$ROOT/Example Presentation/What is Trilium Presenter.mkd"
cp example/before-vs-after.md "$ROOT/Example Presentation/Getting Started.mkd"
cp example/under-the-hood.md "$ROOT/Example Presentation/Markdown and Layouts.mkd"
cp example/how-it-works.md "$ROOT/Example Presentation/Markdown and Layouts/Markdown Syntax.mkd"
cp example/architecture.md "$ROOT/Example Presentation/Markdown and Layouts/Columns and Speaker Notes.mkd"
cp example/image-demo.md "$ROOT/Example Presentation/Images in Slides.mkd"
cp assets/images/workflow.svg "$ROOT/Example Presentation/Images in Slides_workflow.svg"
cp example/presenter-mode.md "$ROOT/Example Presentation/Three Ways to Present.mkd"
cp example/clone-workflow.md "$ROOT/Example Presentation/Reusable Slides.mkd"
cp example/master-library.md "$ROOT/Example Presentation/Reusable Slides/Build a Slide Library.mkd"
cp example/clones-explained.md "$ROOT/Example Presentation/Reusable Slides/How Clones Work.mkd"
cp example/thank-you.md "$ROOT/Example Presentation/Get Started.mkd"

# Themes
mkdir -p "$ROOT/Themes/Default" "$ROOT/Themes/Dark"
cp assets/container-html/Themes.html "$ROOT/Themes.html"
cp assets/container-html/Default-Theme.html "$ROOT/Themes/Default.html"
cp assets/container-html/Dark-Theme.html "$ROOT/Themes/Dark.html"

for theme in default dark; do
    THEME_DIR="$ROOT/Themes/$(echo "$theme" | sed 's/./\U&/')"
    cp "themes/$theme/base.css" "$THEME_DIR/Base.css"
    cp "themes/$theme/title-slide.css" "$THEME_DIR/Title Slide.css"
    cp "themes/$theme/content-slide.css" "$THEME_DIR/Content Slide.css"
    cp "themes/$theme/handout.css" "$THEME_DIR/Handout.css"
    cp "themes/$theme/chapter-slide.css" "$THEME_DIR/Chapter Slide.css"
    cp "assets/backgrounds/$theme/Title Slide_background.svg" "$THEME_DIR/Title Slide_background.svg"
    cp "assets/backgrounds/$theme/Content Slide_background.svg" "$THEME_DIR/Content Slide_background.svg"
done

# Templates
mkdir -p "$ROOT/Templates"
cp assets/container-html/Templates.html "$ROOT/Templates.html"
cp templates/title.md "$ROOT/Templates/Title.mkd"
cp templates/agenda.md "$ROOT/Templates/Agenda.mkd"
cp templates/bullet-points.md "$ROOT/Templates/Bullet Points.mkd"
cp templates/two-columns.md "$ROOT/Templates/Two Columns.mkd"
cp templates/three-columns.md "$ROOT/Templates/Three Columns.mkd"
cp templates/image.md "$ROOT/Templates/Image.mkd"
cp templates/image-with-text.md "$ROOT/Templates/Image with Text.mkd"
cp templates/code.md "$ROOT/Templates/Code.mkd"
cp templates/quote.md "$ROOT/Templates/Quote.mkd"
cp templates/section-break.md "$ROOT/Templates/Chapter.mkd"
cp templates/thank-you.md "$ROOT/Templates/Thank You.mkd"

# Meta
cp meta.json "$OUTDIR/!!!meta.json"

# Build zip
ZIPFILE="trilium-presenter-plugin.zip"
(cd "$OUTDIR" && zip -r - .) > "$ZIPFILE"
rm -rf "$OUTDIR"

echo "Built $ZIPFILE ($VERSION)"
