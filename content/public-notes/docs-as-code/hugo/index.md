---
title: "Hugo"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["hugo", "static-site", "go", "docs-as-code"]
---

Hugo is a static site generator written in Go. Content is Markdown, templates are Go HTML templates, and the output is plain HTML/CSS/JS — no server-side runtime, no database. Build times are fast even for large sites; most builds complete in under a second. This site is built with Hugo.

## Structure

```
content/        # Markdown pages — mirrors the URL structure
layouts/        # Template overrides (Hugo prefers local files over theme files)
assets/         # CSS, JS, images processed by Hugo Pipes
static/         # Files copied as-is into the output
themes/         # Theme(s), typically pulled via Go modules
config.yaml     # Site configuration
```

Content files use YAML front matter to set metadata:

```markdown
---
title: "My Page"
date: 2026-06-04
draft: false
tags: ["example"]
---

Page content here.
```

## Themes via Go modules

Themes are imported as Go modules in `go.mod`. To override a theme template or style, mirror the file path under `layouts/` or `assets/` — Hugo's lookup order prefers local files over theme files, so the override takes effect without touching the theme itself.

## Build and serve

```bash
# Serve locally with draft and future content enabled
hugo server -D --buildFuture

# Build to public/
hugo --minify
```

## Sections and taxonomies

Hugo's content model is built around sections (top-level directories in `content/`) and taxonomies (tags, categories). Each section and taxonomy gets its own listing page automatically. `_index.md` in a section directory controls the listing page's content and front matter.

## Resources

- [Hugo documentation](https://gohugo.io/documentation/)
- [Hugo themes](https://themes.gohugo.io/)
- [Hugo Stack theme](https://github.com/CaiJimmy/hugo-theme-stack) — used by this site
