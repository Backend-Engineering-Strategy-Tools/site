Help write and polish blog posts — edit Markdown files in place, fix prose, and keep content consistent.

## Architecture

**Hugo static site** using the [Hugo Stack theme](https://github.com/CaiJimmy/hugo-theme-stack) (v4, via Go modules), deployed to GitHub Pages.

### Content model

All pages live in `content/` as Markdown with YAML front matter. All use `layout: single` for full-width rendering and `showReadingTime: false`.

### Sections

**`homelab/`** — Narrative, first-person posts about building things in the homelab. Covers what actually happened: the sequence, the dead ends, the workarounds. Tone is conversational and direct.

**`public-notes/`** — Reference material. Factual, structured, distilled. The "how it works" without the personal journey. Tone is neutral and informational.

### Local scratch files

`research/` and `input/` contain uncommitted Markdown files used as raw material when building new sections — notes, data dumps, references. These are never published.

### External PDF assets

CV and cover letter PDFs are pulled from the private `Backend-Engineering-Strategy-Tools/cv` repo at build time via the `BEST_SITE_PAT` secret and placed into `static/cv/`. Not available during local `make serve`.

### Theme customization

Override theme templates or styles by creating files under `layouts/` or `assets/` — Hugo's lookup order prefers local files over theme files.
