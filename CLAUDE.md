# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Serve locally (drafts and future-dated content enabled, http://localhost:1313)
make serve

# Build static site into public/ (minified, via Docker)
make build

# Remove generated output
make clean
```

The Makefile uses Docker (`ghcr.io/gohugoio/hugo:v0.157.0`) for both serving and building, ensuring a consistent environment. Hugo is not required locally.

## Architecture

This is a **Hugo static site** using the [Hugo Stack theme](https://github.com/CaiJimmy/hugo-theme-stack) (v4, via Go modules). It serves as a professional portfolio for "Backend Engineering Strategy Tools" and is deployed to GitHub Pages.

### Content model

All pages live in `content/` as Markdown with YAML front matter. The site has three pages: home (`_index.md`), about, and projects. All use `layout: single` for full-width rendering and have `showReadingTime: false`.

### External PDF assets

The CV and cover letter PDFs are **not stored in this repo**. They are pulled from the private `Backend-Engineering-Strategy-Tools/cv` GitHub repository at **build time** by the GitHub Actions workflow (`.github/workflows/build.yml`) using the `BEST_SITE_PAT` secret. The PDFs are placed into `static/` before Hugo builds, so they end up in `public/cv/`. Local `make serve` will not have these files unless fetched manually.

### Deployment

Pushing to `main` triggers the GitHub Actions workflow which: fetches PDFs → builds with Hugo (extended, minified) → deploys to GitHub Pages at `https://backend-engineering-strategy-tools.github.io/site/`.

### Theme customization

The Stack theme is imported via `go.mod`. To override theme templates or styles, create files under `layouts/` or `assets/` mirroring the theme's structure — Hugo's lookup order will prefer local files over theme files.
