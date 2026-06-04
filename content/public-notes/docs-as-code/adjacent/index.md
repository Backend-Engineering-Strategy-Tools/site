---
title: "Document Tools — Pandoc, LaTeX, Typst, AsciiDoc, Sphinx"
date: 2026-06-04
draft: false
showReadingTime: false
layout: single
tags: ["pandoc", "latex", "typst", "asciidoc", "sphinx", "docs-as-code"]
---

Tools adjacent to the Markdown/Hugo docs-as-code workflow — format conversion, typesetting, heavier markup languages, and documentation generators.

## Pandoc

The universal document converter. Pandoc reads and writes dozens of formats: Markdown, HTML, DOCX, EPUB, LaTeX, RST, AsciiDoc, and more. The most common use in a docs-as-code workflow is converting Markdown to PDF (via LaTeX), to DOCX for stakeholders who need Word files, or to self-contained HTML for offline distribution. A single source in Markdown, multiple output formats on demand. Docker images make it easy to run without a local install — the full LaTeX stack is large but containable.

## LaTeX

A typesetting system built for precision output — academic papers, technical documentation, books. LaTeX gives exact control over typography, equations, cross-references, and bibliography. The source is plain text markup that compiles to PDF. Steep learning curve, verbose syntax, but the output quality for complex documents (especially anything with mathematical notation) is unmatched. Pandoc uses LaTeX as the intermediate format when generating PDFs, so you often interact with LaTeX indirectly through a Pandoc pipeline rather than writing `.tex` directly.

## Typst

A newer alternative to LaTeX with a friendlier syntax and faster compilation. Typst is designed from scratch for the same use case — precise typeset documents, scientific papers, equations — but the markup is more readable and the error messages are useful. Still maturing but gaining traction as a LaTeX replacement for teams starting fresh. Compiles to PDF directly; no intermediate format.

## AsciiDoc

A markup language heavier than Markdown but lighter than LaTeX, designed specifically for technical documentation. AsciiDoc supports cross-references, admonitions (NOTE, WARNING, TIP blocks), includes (assembling a document from multiple source files), and detailed table and image control — things Markdown handles awkwardly or not at all. Asciidoctor is the primary processor (Ruby, with a Java port). Used heavily by Red Hat, the O'Reilly book toolchain, and projects that need a single-source publishing pipeline for both web and print output.

## Sphinx

A documentation generator from the Python ecosystem, originally built for the Python language documentation. Sphinx reads reStructuredText (RST) or Markdown source and produces HTML sites, PDF (via LaTeX), and ePub. The key feature is its cross-referencing system — links between pages, auto-generated API docs from docstrings, and an index are all first-class. The `Read the Docs` hosting platform is built around Sphinx. Common outside Python too for any project that wants a structured documentation site with strong cross-referencing.

## Resources

- [Pandoc documentation](https://pandoc.org/MANUAL.html)
- [Pandoc Docker image](https://hub.docker.com/r/pandoc/latex)
- [LaTeX project](https://www.latex-project.org/)
- [Typst documentation](https://typst.app/docs/)
- [AsciiDoc / Asciidoctor documentation](https://docs.asciidoctor.org/)
- [Sphinx documentation](https://www.sphinx-doc.org/)
