# site

Professional portfolio site — **[backend-engineering-strategy-tools.github.io/site](https://backend-engineering-strategy-tools.github.io/site/)**

Built with [Hugo](https://gohugo.io/) + [Stack theme](https://github.com/CaiJimmy/hugo-theme-stack). Deployed to GitHub Pages on push to `main`.

## Local development

Docker is required; Hugo does not need to be installed locally.

```bash
make serve   # http://localhost:1313 (drafts and future-dated content enabled)
make build   # build into public/ (minified)
make clean   # remove public/
```

## Notes

- The CV and cover letter PDFs are **not stored in this repo** — they are fetched at build time from the private `Backend-Engineering-Strategy-Tools/cv` repo via the `BEST_SITE_PAT` Actions secret. They will be absent during local `make serve`.
- To override theme templates or styles, add files under `layouts/` or `assets/` mirroring the theme's structure.
