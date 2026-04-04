/**
 * Trilium Presenter - Widget
 * Adds a "Present" button to the right panel.
 * Clicking it opens a fullscreen presentation in a new window.
 */

const TPL = `
<div style="padding: 10px; border-bottom: 1px solid var(--main-border-color);">
    <h4 style="margin: 0 0 8px 0;">Trilium Presenter</h4>
    <div style="margin-bottom: 8px;">
        <label style="font-size: 0.85em; color: var(--muted-text-color); display: block; margin-bottom: 2px;">Theme</label>
        <select class="tp-theme-select form-control" style="width: 100%; font-size: 0.9em;">
            <option value="">Loading...</option>
        </select>
    </div>
    <button class="tp-present-btn btn btn-primary btn-sm" style="width: 100%; margin-bottom: 4px;">
        ▶ Present
    </button>
    <button class="tp-presenter-btn btn btn-secondary btn-sm" style="width: 100%; margin-bottom: 4px;">
        🖥 Presenter Mode
    </button>
    <button class="tp-handout-btn btn btn-secondary btn-sm" style="width: 100%;">
        📄 Handout (PDF)
    </button>
    <button class="tp-slide-btn btn btn-secondary btn-sm" style="width: 100%; margin-top: 4px;">
        🔎 Show Slide
    </button>
</div>
`;

class PresenterWidget extends api.NoteContextAwareWidget {
    get position() { return 100; }
    get parentWidget() { return 'right-pane'; }

    doRenderBody()  {
        this.$widget = $(TPL);
        this.$widget.find('.tp-present-btn').on('click', () => this.startPresentation(false));
        this.$widget.find('.tp-presenter-btn').on('click', () => this.startPresentation(true));
        this.$widget.find('.tp-handout-btn').on('click', () => this.startPresentation('handout'));
        this.$widget.find('.tp-slide-btn').on('click', () => this.showSingleSlide());
        return this.$widget;
    }

    async refreshWithNote(note) {
        const hasChildren = note.hasChildren();
        const isSlideable = note.type === 'code' && note.mime === 'text/x-markdown';
        const show = hasChildren || isSlideable;
        this.toggleInt(show);

        if (show) {
            // Presentation buttons only for notes with children
            this.$widget.find('.tp-present-btn, .tp-presenter-btn, .tp-handout-btn').toggle(hasChildren);
            // Theme selector visible for presentations and single slides
            this.$widget.find('.tp-theme-select').closest('div').toggle(hasChildren || isSlideable);
            // Show Slide button for any slideable note
            this.$widget.find('.tp-slide-btn').toggle(isSlideable);

            if (hasChildren || isSlideable) {
                await this.loadThemes(note);
            }
        }
    }

    /**
     * Load available themes into the combobox.
     * Pre-selects: #presenterTheme label value > "Default"
     */
    async loadThemes(note) {
        const $select = this.$widget.find('.tp-theme-select');

        try {
            const themes = await api.runOnBackend(() => {
                const themeNotes = api.searchForNotes('#presenterTheme');
                return themeNotes.map(n => ({
                    noteId: n.noteId,
                    title: n.title
                }));
            });

            $select.empty();

            if (themes.length === 0) {
                $select.append('<option value="">No themes found</option>');
                return;
            }

            for (const theme of themes) {
                $select.append(`<option value="${theme.noteId}">${theme.title}</option>`);
            }

            // Pre-select: "Default" theme
            const defaultTheme = themes.find(t => t.title === 'Default');
            if (defaultTheme) {
                $select.val(defaultTheme.noteId);
            }
        } catch (e) {
            console.error('Failed to load themes:', e);
            $select.empty().append('<option value="">Error loading themes</option>');
        }
    }

    async startPresentation(presenterMode) {
        const noteId = this.noteId;
        const themeNoteId = this.$widget.find('.tp-theme-select').val();

        try {
            // Fetch presentation data from backend
            const data = await api.runOnBackend((rootNoteId, themeId) => {
                const root = api.getNote(rootNoteId);
                if (!root) return { error: 'Note not found' };

                // Read #presenterLang label, fallback to "en"
                const lang = root.getLabelValue('presenterLang') || 'en';

                // Collect slides via depth-first pre-order traversal
                const slides = [];

                function getSortedChildren(note) {
                    const children = note.getChildNotes();
                    const branches = note.getChildBranches();
                    const posMap = {};
                    for (const b of branches) {
                        posMap[b.noteId] = b.notePosition;
                    }
                    children.sort((a, b) => (posMap[a.noteId] || 0) - (posMap[b.noteId] || 0));
                    return children;
                }

                function collectSlides(note, visited) {
                    // Skip non-content types
                    if (note.type === 'image' || note.type === 'file') return;

                    // Guard against circular clones
                    if (visited.has(note.noteId)) return;
                    visited.add(note.noteId);

                    const content = note.getContent() || '';

                    // Skip text/html container notes (empty or HTML-only)
                    if (note.type === 'text') {
                        // Still recurse into children
                        for (const child of getSortedChildren(note)) {
                            collectSlides(child, visited);
                        }
                        return;
                    }
                    const attachments = note.getAttachments ? note.getAttachments() : [];
                    const attInfo = attachments.map(a => ({
                        id: a.attachmentId,
                        title: a.title,
                        url: `api/attachments/${a.attachmentId}/image/${encodeURIComponent(a.title)}`
                    }));

                    // Slide type: #slideType label > fallback (first=title, rest=content)
                    let slideType = note.getLabelValue('slideType');
                    if (!slideType) {
                        slideType = (slides.length === 0) ? 'title' : 'content';
                    }

                    slides.push({
                        noteId: note.noteId,
                        title: note.title,
                        content: content,
                        mime: note.mime,
                        type: slideType,
                        attachments: attInfo
                    });

                    // Recurse into children
                    for (const child of getSortedChildren(note)) {
                        collectSlides(child, visited);
                    }
                }

                const visited = new Set();
                for (const child of getSortedChildren(root)) {
                    collectSlides(child, visited);
                }

                // Load CSS templates from selected theme
                const templates = { base: '', types: {}, handout: '' };
                let templateFolder;

                // Priority 1: Theme selected in widget combobox
                if (themeId) {
                    templateFolder = api.getNote(themeId);
                }

                // Priority 2: Default theme (first note with #presenterTheme label and title "Default")
                if (!templateFolder) {
                    const themeNotes = api.searchForNotes('#presenterTheme');
                    const defaultTheme = themeNotes.find(n => n.title === 'Default');
                    if (defaultTheme) {
                        templateFolder = defaultTheme;
                    } else if (themeNotes.length > 0) {
                        templateFolder = themeNotes[0];
                    }
                }
                if (templateFolder) {
                    const tmplChildren = templateFolder.getChildNotes();
                    for (const tmpl of tmplChildren) {
                        const css = tmpl.getContent() || '';
                        const atts = tmpl.getAttachments ? tmpl.getAttachments() : [];
                        const bgAtt = atts.find(a => a.title === 'background.svg' || a.role === 'image');
                        const bgUrl = bgAtt ? `api/attachments/${bgAtt.attachmentId}/image/${encodeURIComponent(bgAtt.title)}` : '';

                        if (tmpl.title === 'Base') {
                            templates.base = css;
                        } else if (tmpl.title === 'Handout') {
                            templates.handout = { css, bgUrl };
                        } else {
                            const typeName = tmpl.title.replace(/\s*Slide\s*/i, '').trim().toLowerCase();
                            templates.types[typeName] = { css, bgUrl };
                        }
                    }
                }

                return {
                    title: root.title,
                    lang: lang,
                    slideCount: slides.length,
                    slides: slides,
                    templates: templates
                };
            }, [noteId, themeNoteId]);

            if (data.error) {
                api.showError(data.error);
                return;
            }

            if (data.slideCount === 0) {
                api.showError('No slides found. Add child notes to create slides.');
                return;
            }

            // Build and open presentation
            const html = this.buildPresentation(data, presenterMode);
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);

            if (presenterMode) {
                window.open(url, 'trilium-presenter-mode', 'width=1200,height=800');
            } else {
                window.open(url, 'trilium-presentation');
            }
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (e) {
            api.showError(`Presentation failed: ${e.message}`);
            console.error('Trilium Presenter error:', e);
        }
    }

    async showSingleSlide() {
        const noteId = this.noteId;
        const themeNoteId = this.$widget.find('.tp-theme-select').val();

        try {
            const data = await api.runOnBackend((nId, themeId) => {
                const note = api.getNote(nId);
                if (!note) return { error: 'Note not found' };

                const lang = note.getLabelValue('presenterLang') || 'en';
                const content = note.getContent() || '';
                const attachments = note.getAttachments ? note.getAttachments() : [];
                const attInfo = attachments.map(a => ({
                    id: a.attachmentId,
                    title: a.title,
                    url: `api/attachments/${a.attachmentId}/image/${encodeURIComponent(a.title)}`
                }));

                let slideType = note.getLabelValue('slideType') || 'content';

                // Load CSS templates from selected theme
                const templates = { base: '', types: {}, handout: '' };
                let templateFolder;
                if (themeId) {
                    templateFolder = api.getNote(themeId);
                }
                if (!templateFolder) {
                    const themeNotes = api.searchForNotes('#presenterTheme');
                    const defaultTheme = themeNotes.find(n => n.title === 'Default');
                    if (defaultTheme) templateFolder = defaultTheme;
                    else if (themeNotes.length > 0) templateFolder = themeNotes[0];
                }
                if (templateFolder) {
                    const tmplChildren = templateFolder.getChildNotes();
                    for (const tmpl of tmplChildren) {
                        const css = tmpl.getContent() || '';
                        const atts = tmpl.getAttachments ? tmpl.getAttachments() : [];
                        const bgAtt = atts.find(a => a.title === 'background.svg' || a.role === 'image');
                        const bgUrl = bgAtt ? `api/attachments/${bgAtt.attachmentId}/image/${encodeURIComponent(bgAtt.title)}` : '';
                        if (tmpl.title === 'Base') {
                            templates.base = css;
                        } else if (tmpl.title === 'Handout') {
                            templates.handout = { css, bgUrl };
                        } else {
                            const typeName = tmpl.title.replace(/\s*Slide\s*/i, '').trim().toLowerCase();
                            templates.types[typeName] = { css, bgUrl };
                        }
                    }
                }

                return {
                    title: note.title,
                    lang: lang,
                    slideCount: 1,
                    slides: [{
                        noteId: note.noteId,
                        title: note.title,
                        content: content,
                        mime: note.mime,
                        type: slideType,
                        attachments: attInfo
                    }],
                    templates: templates
                };
            }, [noteId, themeNoteId]);

            if (data.error) {
                api.showError(data.error);
                return;
            }

            const html = this.buildPresentation(data, false);
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, 'trilium-presentation');
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (e) {
            api.showError(`Show slide failed: ${e.message}`);
            console.error('Trilium Presenter error:', e);
        }
    }

    /**
     * Convert markdown to HTML (basic implementation).
     * Handles: headings, bold, italic, code blocks, inline code,
     * lists, blockquotes, links, images, horizontal rules, tables.
     */
    markdownToHtml(md) {
        let html = md;

        // Fenced code blocks (``` ... ```) - must be processed BEFORE inline code
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const escaped = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const cls = lang ? ` class="language-${lang}"` : '';
            return `<pre><code${cls}>${escaped.trimEnd()}</code></pre>`;
        });

        // Process line by line for block elements
        const lines = html.split('\n');
        const result = [];
        let inList = false;
        let inOrderedList = false;
        let inBlockquote = false;
        let inTable = false;
        let inPre = false;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];

            // Skip lines inside <pre> blocks
            if (inPre) {
                result.push(line);
                if (line.includes('</pre>')) inPre = false;
                continue;
            }
            if (line.includes('<pre>')) {
                result.push(line);
                if (!line.includes('</pre>')) inPre = true;
                continue;
            }

            // Headings
            if (line.match(/^#{1,6}\s/)) {
                if (inList) { result.push(inOrderedList ? '</ol>' : '</ul>'); inList = false; }
                if (inBlockquote) { result.push('</blockquote>'); inBlockquote = false; }
                const level = line.match(/^(#{1,6})/)[1].length;
                const text = line.replace(/^#{1,6}\s+/, '');
                result.push(`<h${level}>${this.inlineFormat(text)}</h${level}>`);
                continue;
            }

            // Horizontal rule
            if (line.match(/^(-{3,}|\*{3,}|_{3,})$/)) {
                if (inList) { result.push(inOrderedList ? '</ol>' : '</ul>'); inList = false; }
                result.push('<hr>');
                continue;
            }

            // Blockquote
            if (line.match(/^>\s?/)) {
                if (!inBlockquote) { result.push('<blockquote>'); inBlockquote = true; }
                result.push(`<p>${this.inlineFormat(line.replace(/^>\s?/, ''))}</p>`);
                continue;
            } else if (inBlockquote) {
                result.push('</blockquote>');
                inBlockquote = false;
            }

            // Unordered list
            if (line.match(/^[\s]*[-*+]\s/)) {
                if (!inList || inOrderedList) {
                    if (inList) result.push('</ol>');
                    result.push('<ul>');
                    inList = true;
                    inOrderedList = false;
                }
                result.push(`<li>${this.inlineFormat(line.replace(/^[\s]*[-*+]\s+/, ''))}</li>`);
                continue;
            }

            // Ordered list
            if (line.match(/^[\s]*\d+\.\s/)) {
                if (!inList || !inOrderedList) {
                    if (inList) result.push('</ul>');
                    result.push('<ol>');
                    inList = true;
                    inOrderedList = true;
                }
                result.push(`<li>${this.inlineFormat(line.replace(/^[\s]*\d+\.\s+/, ''))}</li>`);
                continue;
            }

            // Close list if we hit a non-list line
            if (inList && line.trim() === '') {
                result.push(inOrderedList ? '</ol>' : '</ul>');
                inList = false;
                continue;
            }

            // Markdown table rows: | ... | ... |
            if (line.trim().match(/^\|(.+)\|$/)) {
                // Skip separator row (|---|---|)
                if (line.trim().match(/^\|[\s\-:|]+\|$/)) {
                    continue;
                }
                const cells = line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
                if (!inTable) {
                    result.push('<table>');
                    result.push('<thead><tr>' + cells.map(c => `<th>${this.inlineFormat(c)}</th>`).join('') + '</tr></thead>');
                    result.push('<tbody>');
                    inTable = true;
                } else {
                    result.push('<tr>' + cells.map(c => `<td>${this.inlineFormat(c)}</td>`).join('') + '</tr>');
                }
                continue;
            } else if (inTable) {
                result.push('</tbody></table>');
                inTable = false;
            }

            // Pass through HTML tags unchanged (e.g. column divs from processPandocDivs)
            if (line.trim().startsWith('<div') || line.trim().startsWith('</div') || line.trim().match(/^<\/?(?:section|table|thead|tbody|tr|th|td|pre|blockquote)/)) {
                result.push(line);
                continue;
            }

            // Paragraph (non-empty lines)
            if (line.trim() !== '') {
                result.push(`<p>${this.inlineFormat(line)}</p>`);
            }
        }

        // Close any open elements
        if (inTable) result.push('</tbody></table>');
        if (inList) result.push(inOrderedList ? '</ol>' : '</ul>');
        if (inBlockquote) result.push('</blockquote>');

        return result.join('\n');
    }

    /**
     * Process inline formatting: bold, italic, code, links, images.
     */
    inlineFormat(text) {
        // Don't process text inside <pre>/<code> tags or placeholders
        if (text.includes('<pre>') || text.includes('<code>')) return text;
        if (text.match(/^<!--\w+-->$/)) return text;

        // Escape HTML entities before processing markdown
        // (preserves markdown syntax characters while preventing raw HTML interpretation)
        text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        // Images with CSS classes: ![alt](src){.class1 .class2}
        text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)\{([^}]+)\}/g, (m, alt, src, attrs) => {
            const classes = attrs.replace(/\./g, '').split(/\s+/).join(' ');
            return `<img alt="${alt}" src="${src}" class="${classes}">`;
        });

        // Images without classes: ![alt](src)
        text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img alt="$1" src="$2">');

        // Links: [text](url)
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

        // Bold + italic: ***text***
        text = text.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');

        // Bold: **text**
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic: *text*
        text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Inline code: `text`
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

        return text;
    }

    /**
     * Process Pandoc-style fenced divs in markdown content.
     * Handles ::: {.columns}, ::: {.column}, ::: {.notes}
     */
    processPandocDivs(content) {
        let notes = '';

        // Extract notes sections (skip fenced code blocks)
        content = content.replace(/(```[\s\S]*?```)|:::+\s*\{\.notes\}([\s\S]*?):::+/g, (m, codeBlock, noteContent) => {
            if (codeBlock) return codeBlock;
            notes = noteContent.trim();
            return '';
        });

        // Remove page breaks (skip fenced code blocks)
        content = content.replace(/(```[\s\S]*?```)|:::+\s*\{\.page-?break\}\s*:::+/g, (m, codeBlock) => {
            if (codeBlock) return codeBlock;
            return '';
        });

        // Process columns — replace with placeholders before markdown processing
        const columnsHtml = [];
        content = this.processColumns(content, columnsHtml);

        // Convert remaining markdown to HTML
        content = this.markdownToHtml(content);

        // Replace placeholders with actual column HTML
        for (let i = 0; i < columnsHtml.length; i++) {
            content = content.replace(`<!--COLUMNS_${i}-->`, columnsHtml[i]);
            // Also handle case where placeholder got wrapped in <p> tags
            content = content.replace(`<p><!--COLUMNS_${i}--></p>`, columnsHtml[i]);
        }

        return { content, notes };
    }

    /**
     * Nesting-aware parser for ::: {.columns} / ::: {.column} blocks.
     * Replaces column blocks with placeholders. The actual HTML is stored
     * in columnsHtml array and swapped back after markdown processing.
     */
    processColumns(content, columnsHtml) {
        const lines = content.split('\n');
        const result = [];
        let i = 0;
        let inCodeBlock = false;

        while (i < lines.length) {
            const line = lines[i];

            // Track fenced code blocks so ::: inside them is not parsed
            if (line.match(/^```/)) {
                inCodeBlock = !inCodeBlock;
                result.push(line);
                i++;
                continue;
            }

            if (!inCodeBlock && line.match(/^:::+\s*\{\.columns\}/)) {
                let depth = 1;
                const block = [];
                i++;

                while (i < lines.length && depth > 0) {
                    const inner = lines[i];
                    if (inner.match(/^:::+\s*\{\./)) {
                        depth++;
                        block.push(inner);
                    } else if (inner.match(/^:::+\s*$/)) {
                        depth--;
                        if (depth > 0) block.push(inner);
                    } else {
                        block.push(inner);
                    }
                    i++;
                }

                // Split block by ::: {.column} markers
                const columnContents = [];
                let currentCol = [];

                for (const bline of block) {
                    if (bline.match(/^:::+\s*\{\.column\}/)) {
                        if (currentCol.length > 0) {
                            columnContents.push(currentCol.join('\n').trim());
                        }
                        currentCol = [];
                    } else if (bline.match(/^:::+\s*$/)) {
                        columnContents.push(currentCol.join('\n').trim());
                        currentCol = [];
                    } else {
                        currentCol.push(bline);
                    }
                }
                if (currentCol.join('').trim()) {
                    columnContents.push(currentCol.join('\n').trim());
                }

                // Build column HTML (each column's markdown is converted here)
                const cols = columnContents.filter(c => c.length > 0);
                const colHtml = cols.map((c, idx) =>
                    `<div class="column column-${idx + 1}">${this.markdownToHtml(c)}</div>`
                ).join('');

                const fullHtml = `<div class="columns columns-${cols.length}">${colHtml}</div>`;
                const idx = columnsHtml.length;
                columnsHtml.push(fullHtml);
                result.push(`<!--COLUMNS_${idx}-->`);
            } else {
                result.push(line);
                i++;
            }
        }

        return result.join('\n');
    }

    /**
     * Resolve attachment filenames to full URLs and process markdown/pandoc.
     * Shared by presentation and handout rendering.
     */
    processSlideContent(slide, baseUrl) {
        let content = slide.content;

        // Resolve attachment filenames to full URLs (skip fenced code blocks)
        const attMap = {};
        for (const att of (slide.attachments || [])) {
            attMap[att.title] = att.url;
        }
        content = content.replace(/(```[\s\S]*?```)|!\[([^\]]*)\]\(([^)]+)\)/g, (match, codeBlock, alt, src) => {
            if (codeBlock) return codeBlock;
            if (!src.startsWith('api/') && !src.startsWith('http') && !src.includes('/')) {
                const resolved = attMap[src];
                if (resolved) {
                    return `![${alt}](${resolved})`;
                }
            }
            return match;
        });

        // Process Pandoc divs (columns, notes) and convert markdown to HTML
        const processed = this.processPandocDivs(content);
        content = processed.content;

        // Fix image URLs - make them absolute so they work in new window
        content = content.replace(/src="api\//g, `src="${baseUrl}/api/`);

        return { content, notes: processed.notes };
    }

    /**
     * Build a complete self-contained HTML presentation.
     */
    buildPresentation(data, presenterMode) {
        const baseUrl = window.location.origin;

        // Handout has its own processing pipeline — return early
        if (presenterMode === 'handout') {
            return this.buildHandoutHtml(data, baseUrl);
        }

        const slides = data.slides;
        const slideElements = [];
        const slideNotes = {};
        const slideTitles = [];

        for (let i = 0; i < slides.length; i++) {
            const slide = slides[i];
            const { content, notes } = this.processSlideContent(slide, baseUrl);

            if (notes) {
                slideNotes[i + 1] = notes;
            }

            const slideClass = `${slide.type}-slide`;
            slideTitles.push(slide.title);

            slideElements.push(`
                <section class="slide ${slideClass}" data-slide="${i + 1}" ${i > 0 ? 'style="display:none"' : ''}>
                    <div class="slide-container">
                        <div class="slide-content">
                            ${content}
                        </div>
                    </div>
                </section>
            `);
        }

        if (presenterMode) {
            return this.buildPresenterHtml(data, slideTitles, slideElements, slideNotes, baseUrl);
        }

        return this.buildPresentationHtml(data, slideElements, slides.length, data.templates || {});
    }

    buildPresentationHtml(data, slideElements, totalSlides, templates) {
        const baseUrl = window.location.origin;
        const lang = data.lang || 'en';

        let css;
        if (templates.base && templates.types) {
            // Build CSS from template notes
            const parts = [templates.base];
            for (const [typeName, tmpl] of Object.entries(templates.types)) {
                if (tmpl.css) parts.push(tmpl.css);
                if (tmpl.bgUrl) {
                    parts.push(`.${typeName}-slide .slide-container { background-image: url('${baseUrl}/${tmpl.bgUrl}'); background-size: cover; background-position: top center; background-repeat: no-repeat; }`);
                }
            }
            css = parts.join('\n');
        } else {
            css = this.getCSS();
        }

        return `<!DOCTYPE html>
<html lang="${lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <style>
        ${css}
    </style>
</head>
<body>
    ${slideElements.join('\n')}
    <script>
        ${this.getNavigationJS(totalSlides)}
    </script>
</body>
</html>`;
    }

    buildPresenterHtml(data, slideTitles, slideElements, slideNotes, baseUrl) {
        const lang = data.lang || 'en';

        // Pre-render speaker notes from markdown to HTML
        const renderedNotes = {};
        for (const [slideNum, notesMd] of Object.entries(slideNotes)) {
            renderedNotes[slideNum] = this.markdownToHtml(notesMd);
        }

        return `<!DOCTYPE html>
<html lang="${lang}">
<head>
    <meta charset="UTF-8">
    <title>${data.title} - Presenter</title>
    <style>
        body { font-family: system-ui, sans-serif; margin: 0; background: #1a1a2e; color: #eee; display: flex; height: 100vh; }
        .main { flex: 2; padding: 20px; display: flex; flex-direction: column; }
        .sidebar { flex: 1; background: #16213e; padding: 20px; overflow-y: auto; border-left: 2px solid #0f3460; }
        .current-info { margin-bottom: 20px; }
        .current-info h2 { color: #e94560; margin: 0 0 5px 0; font-size: 1rem; }
        .current-info h1 { margin: 0; font-size: 1.5rem; }
        .notes-section { flex: 1; background: #16213e; border-radius: 8px; padding: 15px; overflow-y: auto; }
        .notes-section h3 { color: #e94560; margin: 0 0 10px 0; }
        .notes-content { line-height: 1.6; }
        .notes-content ul, .notes-content ol { margin-left: 1.5em; margin-bottom: 0.5em; }
        .notes-content li { margin-bottom: 0.3em; }
        .notes-content p { margin-bottom: 0.5em; }
        .notes-content code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
        .notes-content strong { color: #e94560; }
        .slide-item { padding: 8px 12px; margin: 2px 0; border-radius: 4px; cursor: pointer; }
        .slide-item:hover { background: #0f3460; }
        .slide-item.active { background: #e94560; }
        .slide-num { color: #888; margin-right: 8px; }
        .counter { text-align: center; color: #888; margin-top: 10px; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="main">
        <div class="current-info">
            <h2>Current Slide</h2>
            <h1 id="current-title">${slideTitles[0] || ''}</h1>
        </div>
        <div class="notes-section">
            <h3>Speaker Notes</h3>
            <div class="notes-content" id="notes"></div>
        </div>
        <div class="counter" id="counter">1 / ${slideTitles.length}</div>
    </div>
    <div class="sidebar">
        <h3>Slides</h3>
        <div id="slide-list"></div>
    </div>
    <script>
        const titles = ${JSON.stringify(slideTitles)};
        const notes = ${JSON.stringify(renderedNotes)};
        const total = titles.length;
        let current = 1;
        const channel = new BroadcastChannel('trilium-presenter-sync');

        function updateDisplay() {
            document.getElementById('current-title').textContent = titles[current - 1] || '';
            document.getElementById('counter').textContent = current + ' / ' + total;
            document.getElementById('notes').innerHTML = notes[current] || '<em>No notes for this slide.</em>';
            document.querySelectorAll('.slide-item').forEach((el, i) => {
                el.classList.toggle('active', i === current - 1);
            });
            channel.postMessage({ type: 'navigate', slide: current });
        }

        // Build slide list
        const list = document.getElementById('slide-list');
        titles.forEach((t, i) => {
            const div = document.createElement('div');
            div.className = 'slide-item' + (i === 0 ? ' active' : '');
            div.innerHTML = '<span class="slide-num">' + (i+1) + '</span>' + t;
            div.onclick = () => { current = i + 1; updateDisplay(); };
            list.appendChild(div);
        });

        document.addEventListener('keydown', (e) => {
            if ((e.key === 'ArrowRight' || e.key === ' ') && current < total) { current++; updateDisplay(); }
            if (e.key === 'ArrowLeft' && current > 1) { current--; updateDisplay(); }
            if (e.key === 'Home') { current = 1; updateDisplay(); }
            if (e.key === 'End') { current = total; updateDisplay(); }
        });

        channel.onmessage = (e) => {
            if (e.data.type === 'navigate' && e.data.slide !== current) {
                current = e.data.slide;
                updateDisplay();
            }
        };

        updateDisplay();
    </script>
</body>
</html>`;
    }

    /**
     * Build a printable A4 handout from all slides.
     * Each slide starts on a new page.
     */
    buildHandoutHtml(data, baseUrl) {
        const templates = data.templates || {};
        const lang = data.lang || 'en';

        // Resolve handout CSS — may be string or { css, bgUrl }
        let handoutCSS;
        if (templates.handout && typeof templates.handout === 'object') {
            handoutCSS = templates.handout.css || '';
        } else {
            handoutCSS = templates.handout || '';
        }
        if (!handoutCSS) handoutCSS = this.getHandoutCSS();

        // Process each slide into a document section
        const sections = [];
        for (const slide of data.slides) {
            const { content } = this.processSlideContent(slide, baseUrl);
            sections.push(`<section class="handout-section">${content}</section>`);
        }

        // Page-break rules injected separately so they work regardless of theme CSS
        const layoutCSS = `
            .handout-section { page-break-before: always; break-before: page; }
            .handout-section:first-child { page-break-before: avoid; break-before: avoid; }
        `;

        return `<!DOCTYPE html>
<html lang="${lang}">
<head>
    <meta charset="UTF-8">
    <title>${data.title} — Handout</title>
    <style>${layoutCSS}</style>
    <style>${handoutCSS}</style>
</head>
<body>
    <div class="document-container">
        ${sections.join('\n')}
    </div>
    <script>
        window.onload = () => {
            setTimeout(() => window.print(), 500);
        };
    </script>
</body>
</html>`;
    }

    /**
     * Fallback CSS for handout if no Handout template exists.
     */
    getHandoutCSS() {
        return `
        @page { size: A4 portrait; margin: 2.5cm; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { font-family: 'Segoe UI', system-ui, sans-serif; color: #333; line-height: 1.6; -webkit-print-color-adjust: exact; }
        .document-container { max-width: 100%; padding: 0; }
        .handout-section { page-break-before: always; }
        .handout-section:first-child { page-break-before: avoid; }
        h1 { font-size: 16pt; font-weight: 700; margin: 16pt 0 8pt; color: #1a202c; page-break-after: avoid; }
        h2 { font-size: 14pt; font-weight: 600; margin: 12pt 0 6pt; color: #2d3748; page-break-after: avoid; }
        h3 { font-size: 12pt; font-weight: 600; margin: 10pt 0 5pt; color: #4a5568; page-break-after: avoid; }
        p { margin: 0 0 8pt; line-height: 1.5; font-size: 10pt; color: #374151; text-align: justify; }
        ul, ol { margin: 6pt 0 8pt 20pt; }
        li { font-size: 10pt; line-height: 1.4; margin-bottom: 3pt; color: #374151; }
        pre { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 2pt; padding: 6pt; font-family: monospace; font-size: 8pt; margin: 6pt 0; page-break-inside: avoid; white-space: pre-wrap; }
        code { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 1pt; padding: 1pt 2pt; font-family: monospace; font-size: 8pt; }
        pre code { background: transparent; border: none; padding: 0; }
        table { width: 100%; border-collapse: collapse; margin: 10pt 0; page-break-inside: avoid; font-size: 9pt; }
        th, td { border: 1pt solid #ddd; padding: 6pt 8pt; text-align: left; }
        th { background: #f8f9fa; font-weight: bold; }
        img { max-width: 100%; height: auto; display: block; margin: 10pt auto; page-break-inside: avoid; }
        blockquote { border-left: 2pt solid #3498db; padding: 4pt 8pt; margin: 6pt 0; background: #f8f9fa; font-style: italic; font-size: 9pt; }
        strong { color: #2d3748; font-weight: 600; }
        em { color: #3b82f6; }
        a { color: #2c3e50; text-decoration: underline; }
        .columns { display: flex; gap: 8pt; margin: 6pt 0; }
        .column { flex: 1; min-width: 0; }
        .page-break { page-break-before: always; }
        @media print { html, body { background: transparent; } }
        `;
    }

    /**
     * Minimal CSS for presentation (inline).
     */
    getCSS() {
        return `
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; overflow: hidden; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }

        .slide { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; }
        .slide-container { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
        .slide-content { width: 100%; max-width: 1600px; padding: 60px 120px; }

        /* Title slide */
        .title-slide { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #eee; }
        .title-slide h1 { font-size: 3.5rem; font-weight: 600; margin-bottom: 0.5em; }
        .title-slide h2 { font-size: 2rem; font-weight: 400; color: #a0aec0; margin-bottom: 0.5em; }
        .title-slide p, .title-slide em { font-size: 1.3rem; color: #a0aec0; }
        .title-slide .slide-content { text-align: center; }

        /* Content slide */
        .content-slide { background: #ffffff; color: #2d3748; }
        .content-slide h1 { font-size: 2.5rem; font-weight: 600; margin-bottom: 1rem; color: #1a202c; }
        .content-slide h2 { font-size: 2rem; font-weight: 500; margin-bottom: 0.8rem; color: #1a202c; }
        .content-slide h3 { font-size: 1.4rem; font-weight: 500; margin-bottom: 0.5rem; color: #2d3748; }
        .content-slide p { font-size: 1.2rem; line-height: 1.6; margin-bottom: 0.8rem; color: #374151; }
        .content-slide ul, .content-slide ol { font-size: 1.2rem; margin-left: 1.5em; margin-bottom: 0.8rem; }
        .content-slide li { margin-bottom: 0.4rem; line-height: 1.5; }
        .content-slide blockquote { border-left: 4px solid #3b82f6; padding: 0.5em 1em; margin: 1em 0; background: #f0f4ff; border-radius: 0 6px 6px 0; }
        .content-slide blockquote p { color: #4a5568; font-style: italic; }
        .content-slide hr { border: none; border-top: 2px solid #e2e8f0; margin: 1.5rem 0; }
        .content-slide a { color: #3b82f6; }

        /* Code */
        pre { background: #1a1a2e; color: #e2e8f0; padding: 1em; border-radius: 8px; overflow-x: auto; margin: 1em 0; }
        code { font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 0.85em; }
        p code, li code { background: #f1f5f9; color: #e94560; padding: 2px 6px; border-radius: 4px; }

        /* Columns */
        .columns { display: grid; gap: 2rem; width: 100%; margin: 1rem 0; }
        .columns-2 { grid-template-columns: 1fr 1fr; }
        .columns-3 { grid-template-columns: 1fr 1fr 1fr; }
        .columns-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }

        /* Images */
        img { max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .img-tiny { height: 4rem; width: auto; }
        .img-small { height: 8rem; width: auto; }
        .img-medium { height: 12rem; width: auto; }
        .img-large { height: 24rem; width: auto; }
        .img-xlarge { height: 30rem; width: auto; }
        .center { display: block; margin-left: auto; margin-right: auto; }

        /* Progress bar */
        .progress-bar { position: fixed; bottom: 0; left: 0; height: 5px; background: #3b82f6; transition: width 0.3s; z-index: 100; }

        /* Navigation hint */
        .nav-hint { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); color: #999; font-size: 0.85rem; opacity: 0; transition: opacity 0.5s; }
        .nav-hint.visible { opacity: 1; }
        `;
    }

    /**
     * Navigation JavaScript (inline in presentation).
     */
    getNavigationJS(totalSlides) {
        return `
        (function() {
            let current = 1;
            const total = ${totalSlides};
            const channel = new BroadcastChannel('trilium-presenter-sync');

            // Progress bar
            const bar = document.createElement('div');
            bar.className = 'progress-bar';
            document.body.appendChild(bar);

            // Navigation hint
            const hint = document.createElement('div');
            hint.className = 'nav-hint';
            hint.textContent = '← → Navigate | Esc Fullscreen';
            document.body.appendChild(hint);
            hint.classList.add('visible');
            setTimeout(() => hint.classList.remove('visible'), 3000);

            function showSlide(n) {
                if (n < 1 || n > total) return;
                document.querySelectorAll('.slide').forEach(s => s.style.display = 'none');
                document.querySelector('[data-slide="' + n + '"]').style.display = '';
                current = n;
                bar.style.width = (current / total * 100) + '%';
                channel.postMessage({ type: 'navigate', slide: current });
            }

            document.addEventListener('keydown', (e) => {
                switch(e.key) {
                    case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown':
                        e.preventDefault(); showSlide(current + 1); break;
                    case 'ArrowLeft': case 'ArrowUp': case 'Backspace': case 'PageUp':
                        e.preventDefault(); showSlide(current - 1); break;
                    case 'Home': e.preventDefault(); showSlide(1); break;
                    case 'End': e.preventDefault(); showSlide(total); break;
                    case 'Escape':
                        if (document.fullscreenElement) document.exitFullscreen();
                        else document.documentElement.requestFullscreen().catch(() => {});
                        break;
                    case 'h': case '?':
                        hint.classList.add('visible');
                        setTimeout(() => hint.classList.remove('visible'), 3000);
                        break;
                }
            });

            // Sync with presenter
            channel.onmessage = (e) => {
                if (e.data.type === 'navigate' && e.data.slide !== current) {
                    showSlide(e.data.slide);
                }
            };

            // Click navigation (skip links and interactive elements)
            document.addEventListener('click', (e) => {
                if (e.target.closest('a, button, input, textarea, select')) return;
                if (e.clientX > window.innerWidth / 2) showSlide(current + 1);
                else showSlide(current - 1);
            });

            showSlide(1);
        })();
        `;
    }
}

module.exports = new PresenterWidget();
