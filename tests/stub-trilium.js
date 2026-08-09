/**
 * The smallest Trilium the widget needs in order to be require()d.
 *
 * `src/widget.js` is a Trilium frontend note: it resolves `api` at class-
 * definition time (`class … extends api.NoteContextAwareWidget`) and exports an
 * instance, so a bare require() in node throws before a single method exists.
 * Two stubs are enough to get past that — after which every pure helper on the
 * instance is directly callable.
 *
 * Deliberately not a DOM: these tests cover the string-producing helpers, which
 * is where the escaping lives. Anything touching the widget's UI or the
 * presentation window belongs in a browser, and the repo rule already says
 * widget behaviour is verified by running it in Trilium.
 */
const calls = { showError: [], searchForNotes: [], getNote: [] };

globalThis.api = {
    NoteContextAwareWidget: class {
        toggleInt() {}
    },
    showError(message) { calls.showError.push(message); },
    async searchForNotes(query) { calls.searchForNotes.push(query); return []; },
    async getNote(id) { calls.getNote.push(id); return null; },
};

globalThis.$ = () => ({
    find: () => ({ on() {}, prop() {}, empty() {}, append() {}, val: () => '' }),
});

// buildPresentation reads window.location.origin to absolutise image URLs.
globalThis.window = { location: { origin: 'https://trilium.example.net' } };

module.exports = { calls };
