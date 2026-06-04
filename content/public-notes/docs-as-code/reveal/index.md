---
title: "Reveal.js"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["reveal", "hugo", "presentations", "docs-as-code", "reveal.js", "decktape"]
---

Reveal.js is a browser-based presentation framework. Slides are HTML rendered in a browser — transitions, speaker notes, code highlighting, nested slides, and a presenter view all included. The source can be plain HTML or Markdown. Stored in Git, versioned, diffable, buildable in CI. No PowerPoint, no Keynote, no binary blobs.

The practical workflow for a docs-as-code setup: write slides in Markdown, serve with Hugo using the Reveal Hugo theme, export to PDF with DeckTape for distribution.

## Hugo integration — Reveal Hugo

[Reveal Hugo](https://github.com/dzello/reveal-hugo) is a Hugo theme that turns a Hugo site into a Reveal.js presentation builder. Add the theme, create a content directory, and Hugo renders each section as a Reveal.js presentation.

Slides live in a Hugo content directory. Horizontal slides are separated by `---`, vertical slides (a column within a section) by `___`:

```markdown
+++
title = "My Talk"
outputs = ["Reveal"]
+++

# First slide

---

# Second slide

Horizontal neighbour of the first.

___

## Second slide, vertical child

Press down to reach this one.

---

# Third slide
```

`outputs = ["Reveal"]` in the front matter tells Hugo to use the Reveal layout instead of the standard page layout.

## Configuration

Reveal.js options set in `config.yaml` under `[params.reveal_hugo]`:

```yaml
params:
  reveal_hugo:
    theme: "black"
    highlight_theme: "monokai"
    slide_number: true
    transition: "slide"
```

Per-slide overrides go in a front matter block on that slide.

## Shortcodes

Reveal Hugo provides shortcodes for Reveal.js features:

```markdown
{{</* slide background-image="bg.jpg" */>}}

# Slide with background image

{{</* /slide */>}}
```

```markdown
{{%/* note */%}}
Speaker notes — visible in presenter mode, not on screen.
{{%/* /note */%}}
```

## Exporting to PDF with DeckTape

DeckTape drives a headless browser through each slide and captures a PDF that preserves the rendered layout — fonts, colours, syntax highlighting. The simplest path is Docker:

```bash
# Export from a live URL
docker run --rm -t -v $(pwd):/slides \
  astefanutti/decktape \
  https://example.com/my-presentation slides.pdf

# Export from a local Hugo server (hugo server running on 1313)
docker run --rm -t --net=host -v $(pwd):/slides \
  astefanutti/decktape \
  http://localhost:1313/presentations/my-talk/ slides.pdf
```

DeckTape auto-detects the presentation framework. Override the output size with `--size 1920x1080` if needed.

## Resources

- [Reveal.js documentation](https://revealjs.com/)
- [Reveal Hugo documentation](https://github.com/dzello/reveal-hugo)
- [DeckTape GitHub](https://github.com/astefanutti/decktape)
