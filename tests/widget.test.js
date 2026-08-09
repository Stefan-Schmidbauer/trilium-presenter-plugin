/**
 * Escaping in the presenter widget.
 *
 * Why this matters more than it looks: the presentation is opened from a blob:
 * URL, and a blob: URL inherits the origin of the document that created it — so
 * the presentation window is same-origin with Trilium. Anything that escapes
 * its context there runs with the user's session.
 *
 * The three helpers cover three different contexts, and using the wrong one is
 * as bad as using none: HTML escaping inside a <script> block still lets
 * `</script>` through, and JSON escaping inside a <style> block does nothing.
 *
 * Run with:  node --test
 */
require('./stub-trilium.js');

const test = require('node:test');
const assert = require('node:assert');

const widget = require('../src/widget.js');

const BREAKOUTS = [
    '</script><img src=x onerror=alert(1)>',
    '</SCRIPT><IMG SRC=x ONERROR=alert(1)>',
    '</style><script>alert(1)</script>',
    '"><script>alert(1)</script>',
    "'; alert(1); //",
];

// ── esc: text and attribute contexts ─────────────────────────────────────────

test('esc covers both quote characters', () => {
    assert.strictEqual(widget.esc('<a href="x">'), '&lt;a href=&quot;x&quot;&gt;');
    assert.strictEqual(widget.esc("it's"), 'it&#39;s');
});

test('esc escapes the ampersand first, so entities are not double-decoded', () => {
    assert.strictEqual(widget.esc('&lt;'), '&amp;lt;');
});

test('esc leaves no angle bracket behind', () => {
    for (const payload of BREAKOUTS) {
        const out = widget.esc(payload);
        assert.ok(!out.includes('<'), payload);
        assert.ok(!out.includes('>'), payload);
    }
});

test('esc tolerates null and undefined', () => {
    assert.strictEqual(widget.esc(null), '');
    assert.strictEqual(widget.esc(undefined), '');
});

// ── escJson: inline <script> context ─────────────────────────────────────────

test('escJson prevents a title from closing the script block', () => {
    // JSON.stringify does not escape `/`, so `</script>` inside a string value
    // ends the block and turns everything after it into markup.
    for (const payload of BREAKOUTS) {
        const out = widget.escJson([payload]);
        assert.ok(!/<\/\s*script/i.test(out), `closed <script> with: ${payload}`);
    }
});

test('escJson keeps the value identical after parsing', () => {
    // Escaping must not change what the presentation actually displays.
    const values = ['plain', 'Ümläute & <b>', 'a</script>b', '', 'ün\\ic\tode'];
    assert.deepStrictEqual(JSON.parse(widget.escJson(values)), values);
});

test('escJson handles the notes object, not just arrays', () => {
    const notes = { 1: '<p>note</p>', 2: '</script>' };
    assert.deepStrictEqual(JSON.parse(widget.escJson(notes)), notes);
});

// ── escStyle: inline <style> context ─────────────────────────────────────────

test('escStyle neutralises anything that could close the style element', () => {
    for (const payload of BREAKOUTS) {
        const out = widget.escStyle(payload);
        assert.ok(!/<\/\s*style/i.test(out), `closed <style> with: ${payload}`);
        assert.ok(!/<\/\s*script/i.test(out), `closed <script> with: ${payload}`);
    }
});

test('escStyle leaves ordinary CSS untouched', () => {
    const css = '@page { size: A4 landscape } .title-slide { content: "a/b" } /* c */';
    assert.strictEqual(widget.escStyle(css), css);
});

test('escStyle tolerates null and undefined', () => {
    assert.strictEqual(widget.escStyle(null), '');
    assert.strictEqual(widget.escStyle(undefined), '');
});

// ── the generated documents ──────────────────────────────────────────────────

function presentation(overrides = {}) {
    return widget.buildPresentation({
        title: 'Deck',
        lang: 'en',
        slideCount: 1,
        slides: [{ noteId: 'n1', title: 'Slide', content: '# Slide', mime: 'text/x-markdown',
                   type: 'content', attachments: [] }],
        templates: {},
        ...overrides,
    }, false);
}

test('a hostile deck title cannot break out of <title>', () => {
    const html = presentation({ title: '</title><script>alert(1)</script>' });
    assert.ok(!html.includes('<script>alert(1)</script>'));
});

test('a hostile presenterLang cannot break out of the lang attribute', () => {
    const html = presentation({ lang: 'en" onload="alert(1)' });
    assert.ok(!html.includes('onload="alert(1)"'));
    assert.ok(html.includes('&quot;'));
});

test('a hostile slideType cannot break out of the class attribute', () => {
    const html = presentation({
        slides: [{ noteId: 'n1', title: 'S', content: 'x', mime: 'text/x-markdown',
                   type: 'content" onmouseover="alert(1)', attachments: [] }],
    });
    assert.ok(!html.includes('onmouseover="alert(1)"'));
});

test('presenter mode embeds slide titles without letting them end the script', () => {
    const html = widget.buildPresentation({
        title: 'Deck',
        lang: 'en',
        slideCount: 1,
        slides: [{ noteId: 'n1', title: '</script><img src=x onerror=alert(1)>',
                   content: 'body', mime: 'text/x-markdown', type: 'content', attachments: [] }],
        templates: {},
    }, true);

    // Exactly the script blocks the template itself opens — the payload added none.
    const opened = (html.match(/<script>/g) || []).length;
    const closed = (html.match(/<\/script>/g) || []).length;
    assert.strictEqual(opened, closed);
    assert.ok(!html.includes('<img src=x onerror=alert(1)>'));
});

test('presenter mode builds the slide list without innerHTML', () => {
    // Titles reach the sidebar as text nodes; innerHTML there would turn markup
    // in a title into live elements.
    const html = widget.buildPresentation({
        title: 'Deck', lang: 'en', slideCount: 1,
        slides: [{ noteId: 'n1', title: 'S', content: 'x', mime: 'text/x-markdown',
                   type: 'content', attachments: [] }],
        templates: {},
    }, true);
    assert.ok(html.includes('createTextNode'));
    assert.ok(!/div\.innerHTML\s*=/.test(html));
});
