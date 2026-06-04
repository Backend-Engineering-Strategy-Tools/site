---
title: "Site Navigation — Beyond the Menu"
date: 2026-06-04
draft: false
showReadingTime: false
tags: ["search", "navigation", "ux", "knowledge-base"]
---

A menu works when the content is shallow and the audience knows what they want. It breaks down when the content grows into something more like a knowledge base — when you have 80 notes across 12 sections and the useful thing is not finding a specific page but discovering that two ideas are connected.

There are a few distinct problems here and they need different tools.

---

## Retrieval vs exploration

**Retrieval** is when you know what you want: "where did I write about Terragrunt?" A search box solves this. Fuzzy matching, title weighting, done.

**Exploration** is when you do not know what you want, or want to rediscover something you wrote a while ago. A menu does not help. Search does not help — you cannot search for something you have forgotten exists.

The menu is for retrieval by navigation. Search is for retrieval by keyword. Neither is for exploration.

---

## What does not work

**Most recently used / most popular** — this feels like someone keeps moving your things. The notes that surface are the ones you or others have looked at lately, not the ones that are useful to you now. Navigation should not have memory that works against you.

**Alphabetical listing** — fine as a fallback, not useful as a primary navigation mode. Proximity means nothing.

---

## Two experiments

### Mindmap

Every note as a node. Edges connect notes that share tags or belong to the same section. Lay it out with a force-directed simulation and you get a visual map of the knowledge base — clusters emerge naturally, isolated notes stand out, and you can trace paths between related ideas.

The interesting property: clicking on one note shows which other notes it is connected to. This is not search — you are not looking for something specific, you are seeing the neighbourhood of an idea.

[Try it →](/public-notes/mindmap/)

### Word cloud

Sections and tags, sized by how many notes carry them. The big words are the areas where there is the most material. Click a word and it feeds directly into the search.

This is an overview of the shape of the knowledge base. Good for answering "what is actually in here?" in a few seconds.

[Try it →](/public-notes/wordcloud/)

---

## The shared data model

Both visualisations run off the same JSON index that powers search — a build-time output from Hugo listing every note with its title, URL, section, tags, and summary. One data source, three interfaces.

The technical implementation is in [Notes: Site Navigation](/public-notes/docs-as-code/site-navigation/).

---

## What is still missing

Tags are sparse — most notes do not have them, so the mindmap edges are mostly section-based rather than cross-section. Adding tags to notes as they are written would make the mindmap significantly more interesting over time.

The word cloud currently surfaces sections more than tags for the same reason. As tags accumulate, it will shift toward showing the actual concepts rather than just the categories.

Both are experiments. The interesting question is whether they change how notes get written — if knowing that a note will appear in a connected graph encourages tagging, or whether tagging feels like overhead.
