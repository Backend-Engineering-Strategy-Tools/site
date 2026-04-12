---
name: Hugo Stack theme image setup
description: Stack theme requires page bundles for images — render hook override was rejected in favour of page bundles
type: feedback
---

Use **page bundles** for all content with images. The Stack theme's render hook (`layouts/_markup/render-image.html`) uses `.Page.Resources.Get` — it only finds images co-located with the page, not from `assets/` or `static/`.

**Why:** User explicitly chose page bundles over a render hook override after understanding the tradeoff. Render hook approach was offered twice and declined.

**How to apply:**
- Every note is a folder with `index.md` + images alongside it
- Image references in markdown use relative paths: `![alt](filename.png)` not `![alt](/images/filename.png)`
- Do not suggest moving images to `assets/` or `static/` for use in notes — it won't work with this theme
- If a new note needs images, create it as a bundle from the start
