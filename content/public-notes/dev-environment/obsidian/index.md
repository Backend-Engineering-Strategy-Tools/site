---
title: "Obsidian"
date: 2026-06-04
draft: false
showReadingTime: false
layout: single
tags: ["obsidian", "markdown", "pkm", "notes", "dev-environment"]
---

Obsidian is a local-first Markdown note-taking and knowledge management tool. Notes are plain `.md` files in a folder on disk — your vault. No proprietary format, no cloud lock-in, no account required. Open the folder in any text editor and the files are right there.

The core feature is bidirectional linking: `[[note name]]` creates a link between notes, and Obsidian builds a graph of all connections. This makes it useful for capturing ideas that relate to each other — architecture decisions, research, running notes on a project — without forcing a rigid folder hierarchy upfront.

Plugins extend the core significantly. Community plugins cover daily notes, task management, canvas (spatial note layout), Dataview (query your vault like a database), Git sync, and more.

For a dev workflow, a common setup is a vault in a Git repository — plain Markdown means diffs are readable, history is useful, and syncing across machines is standard Git push/pull.

## Resources

- [Obsidian documentation](https://help.obsidian.md/)
- [Obsidian community plugins](https://obsidian.md/plugins)
