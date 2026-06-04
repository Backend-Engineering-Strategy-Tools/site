---
title: "Markdown"
draft: false
date: 2024-01-01
showReadingTime: false
layout: single
tags: ["markdown", "docs-as-code", "writing"]
---

Markdown is a lightweight markup language that converts to HTML. The syntax is designed to be readable as plain text — a `# Heading` looks like a heading even in a text editor, and `**bold**` reads naturally. John Gruber created the original spec in 2004; CommonMark later formalised an unambiguous specification. GitHub Flavored Markdown (GFM) extends CommonMark with tables, task lists, and syntax-highlighted fenced code blocks.

## Core syntax

```markdown
# Heading 1
## Heading 2

**bold**  *italic*  `inline code`

- unordered list item
- another item
  - nested item

1. ordered list
2. second item

[link text](https://example.com)
![alt text](image.png)

> blockquote

---   (horizontal rule)
```

## Code blocks

Fenced code blocks with a language identifier get syntax highlighting in most renderers:

````markdown
```go
func main() {
    fmt.Println("hello")
}
```
````

## Tables (GFM)

```markdown
| Column 1 | Column 2 |
|---|---|
| value    | value    |
```

Alignment is controlled by colons in the separator row: `|:---|` left, `|---:|` right, `|:---:|` centre.

## Front matter

Static site generators (Hugo, Jekyll) extend Markdown with YAML front matter — a metadata block delimited by `---` at the top of the file. Hugo uses it for titles, dates, tags, and draft status; it is not part of the Markdown spec but is the universal convention in docs-as-code workflows.

## Resources

- [CommonMark specification](https://spec.commonmark.org/)
- [GitHub Flavored Markdown specification](https://github.github.com/gfm/)
- [Markdown guide](https://www.markdownguide.org/)
