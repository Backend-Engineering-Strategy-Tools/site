    ---
title: "Site Navigation"
date: 2026-06-04
draft: false
showReadingTime: false
layout: single
---

Technical reference for the search, mindmap, and word cloud navigation on this site. The design approach is in [Thinking: Site Navigation — Beyond the Menu](/thinking/site-navigation/).

---

## Architecture overview

Three navigation modes, one data source:

```
Hugo build
  └── list.json.json template
        └── /public-notes/index.json   ← built once
              ├── search.js (Fuse.js)
              ├── mindmap.js (D3.js)
              └── wordcloud.js (wordcloud2.js)
```

All three run entirely client-side. No server, no external search service. Hugo generates a JSON index at build time; JavaScript fetches it and does the rest.

---

## The JSON index

Hugo outputs a JSON file for the public-notes section via a custom output format. The `_index.md` for the section declares both HTML and JSON outputs:

```yaml
outputs:
  - HTML
  - JSON
```

The template at `layouts/public-notes/list.json.json` iterates all published pages recursively:

```
{{- $pages := where .RegularPagesRecursive "Draft" false -}}
[
{{- range $i, $page := $pages -}}
{{- if $i }},{{ end }}
{"title":{{ $page.Title | jsonify }},
 "url":{{ $page.RelPermalink | jsonify }},
 "section":{{ $page.Section | jsonify }},
 "subsection":{{ index (split $page.RelPermalink "/") 2 | jsonify }},
 "tags":{{ $page.Params.tags | default slice | jsonify }},
 "summary":{{ $page.Summary | plainify | truncate 160 | jsonify }}}
{{- end }}
]
```

Available at `/public-notes/index.json` after build. Each entry:

| Field | Content |
|-------|---------|
| `title` | Page title |
| `url` | Relative URL |
| `section` | Top-level section (`public-notes`) |
| `subsection` | Second path segment (e.g. `infra-as-code`) |
| `tags` | Array from front matter, empty array if none |
| `summary` | Auto-generated from first ~160 chars of content |

---

## Search — Fuse.js

[Fuse.js](https://www.fusejs.io/) is a lightweight fuzzy-search library. It runs entirely in the browser against the JSON index — no server, no indexing step at build time beyond what Hugo already produces.

**Initialisation:**

```javascript
fetch('/public-notes/index.json')
  .then(r => r.json())
  .then(data => {
    const fuse = new Fuse(data, {
      keys: [
        { name: 'title',      weight: 3 },
        { name: 'tags',       weight: 2 },
        { name: 'subsection', weight: 1.5 },
        { name: 'summary',    weight: 1 }
      ],
      threshold: 0.35,   // 0 = exact, 1 = match anything
      includeScore: true
    });
  });
```

Title matches rank highest, followed by tags, then section, then summary text. `threshold: 0.35` allows minor typos and partial matches without returning garbage.

**Trade-offs vs alternatives:**

- **Fuse.js** — zero build-time overhead, smallest setup, good enough for ~100 notes. Gets slower with very large corpora.
- **Pagefind** — generates its own index at build time, better at full-text search, needs a build step integration. Worth switching to if the notes grow large enough that Fuse becomes slow.
- **Lunr.js** — similar to Fuse, slightly more powerful query syntax, heavier.

Implemented as a Hugo shortcode (`layouts/shortcodes/search-notes.html`) — the CDN script, input, results container, and JS logic are all inline, same pattern as the carousel shortcode.

---

## Mindmap — D3.js force simulation

[D3.js](https://d3js.org/) force simulation lays out notes as nodes connected by edges. Nodes are coloured by subsection. Edges connect notes that share tags (strong) or belong to the same subsection (light).

**Data model:**

```javascript
// nodes: one per page
const nodes = data.map(p => ({
  id: p.url, title: p.title,
  section: p.subsection, tags: p.tags
}));

// edges: shared tags (strength 0.8) or same subsection (strength 0.15)
const links = [];
for (let i = 0; i < nodes.length; i++) {
  for (let j = i+1; j < nodes.length; j++) {
    const sharedTags = nodes[i].tags.filter(t => nodes[j].tags.includes(t));
    if (sharedTags.length) {
      links.push({ source: nodes[i].id, target: nodes[j].id, strength: 0.8 });
    } else if (nodes[i].section === nodes[j].section) {
      links.push({ source: nodes[i].id, target: nodes[j].id, strength: 0.15 });
    }
  }
}
```

**Forces:**

```javascript
d3.forceSimulation(nodes)
  .force('link',      d3.forceLink(links).id(d => d.id)
                        .strength(l => l.strength).distance(80))
  .force('charge',    d3.forceManyBody().strength(-120))
  .force('center',    d3.forceCenter(W/2, H/2))
  .force('collision', d3.forceCollide().radius(18))
```

**Interaction:** click a node to highlight its direct neighbours and hide unrelated edges. Click the background to reset. Drag nodes to rearrange. Scroll to zoom (zoom is applied to a `<g>` transform via `d3.zoom`).

**Current limitation:** most notes do not have tags in their front matter, so edges are mostly section-based. The graph becomes more useful as tags are added. Adding `tags:` to front matter of any note immediately creates cross-section connections in the mindmap.

---

## Word cloud — wordcloud2.js

[wordcloud2.js](https://github.com/timdream/wordcloud2.js/) renders a canvas-based word cloud. Words are sections and tags from the index, sized by frequency.

**Frequency counting:**

```javascript
const counts = {}, sectionOf = {};
data.forEach(page => {
  const sub = page.subsection || page.section;
  counts[sub] = (counts[sub] || 0) + 3;  // sections weight more
  sectionOf[sub] = sub;
  page.tags.forEach(tag => {
    counts[tag] = (counts[tag] || 0) + 1;
    if (!sectionOf[tag]) sectionOf[tag] = sub;
  });
});
```

Sections are weighted 3× per page so they appear prominently even with sparse tags. Tags accumulate naturally as notes get tagged.

**Click behaviour:** clicking a word feeds it into the search input on the search page (if present on the same page) or navigates to `/public-notes/search/`.

---

## Section colour map

Both mindmap and word cloud use the same colour map:

| Section | Colour |
|---------|--------|
| infra-as-code | `#4CAF50` green |
| cloud-infrastructure | `#2196F3` blue |
| cicd | `#FF9800` amber |
| languages | `#9C27B0` purple |
| networking | `#00BCD4` cyan |
| security | `#F44336` red |
| observability | `#FF5722` deep orange |
| frameworks-tools | `#795548` brown |
| dev-environment | `#607D8B` blue-grey |
| docs-as-code | `#E91E63` pink |
| ai | `#673AB7` deep purple |
| hardware | `#8BC34A` light green |

When a new section is added, add it to the colour map in both shortcodes (`mindmap-notes.html` and `wordcloud-notes.html`).

---

## Adding tags to notes

Tags are the key input that makes cross-section connections appear in the mindmap. Add them to any note's front matter:

```yaml
---
title: "Terraform"
tags: ["iac", "terraform", "hcl", "state-management"]
---
```

Notes that share tags will be connected across section boundaries in the mindmap. The word cloud will show the tags sized by how many notes carry them.

No rebuild of the shortcode or template is needed — the JSON template picks up tags automatically at build time.
