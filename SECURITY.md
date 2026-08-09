# Security Policy

## Reporting a vulnerability

Please report security issues **privately**, through GitHub's private
vulnerability reporting: open the
[Security tab](https://github.com/Stefan-Schmidbauer/trilium-presenter-plugin/security)
of this repository and use **Report a vulnerability**. That opens a private
advisory visible only to you and the maintainer.

Please do not open a public issue for a vulnerability, and do not include a
working ETAPI token in the report — describe the setup instead.

This is a spare-time project maintained by one person. Expect an initial reply
within about a week; there is no guaranteed fix window.

## Supported versions

Only the latest commit on `main` is supported. There are no backports to tags.

## Scope

This plugin is frontend-only code that runs inside Trilium and opens the
presentation in a second window via a `blob:` URL. A `blob:` URL inherits the
origin of the document that created it, so that window is **same-origin with
Trilium** and anything executing there can act as the logged-in user. Reports
about a way to get script execution into it are in scope, in particular:

- a slide title, note title, or speaker note that escapes its context in the
  generated presentation — the inline `<script>` block, the `<title>` element,
  or the `<style>` block
- theme CSS that breaks out of the `<style>` element

Known and documented, so **not** a finding on their own:

- Trilium has no user separation: anyone who can write notes in the instance
  already has full access, so "a malicious note can do X" is only interesting
  where the note could arrive from elsewhere — a sync peer, or an imported
  subtree
- speaker notes are rendered as HTML on purpose, so markdown in them can produce
  markup
