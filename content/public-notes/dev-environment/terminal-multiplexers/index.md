---
title: "Terminal Multiplexers"
description: "tmux vs Zellij comparison — and why plain terminal tabs are still the right call for now."
date: 2026-05-12
draft: false
tags: ["terminal", "multiplexer", "cli", "tools", "tmux", "zellij"]
showReadingTime: false
layout: single
---

This note explores the choice between `Zellij` and `tmux` for terminal multiplexing.

## Why use a terminal multiplexer?

Terminal multiplexers allow you to run multiple terminal sessions within a single window, detach from them, and reattach later. This is incredibly useful for:

- Persistent sessions (e.g., long-running processes continue even if your SSH connection drops).
- Organizing multiple tasks (tabs, panes).
- Remote development.

## Tmux

https://github.com/tmux/tmux

**Introduction:** `tmux` is a long-standing and extremely powerful terminal multiplexer. It's highly configurable and has a vast user base.

**Pros:**
- Mature and stable.
- Very flexible and customizable.
- Widely adopted, lots of resources and plugins.

**Cons:**
- Configuration can be complex and requires significant effort to set up to personal taste.
- Default keybindings can be arcane.
- Can feel a bit dated in terms of user experience compared to newer alternatives.

## Zellij

https://zellij.dev/

**Introduction:** `Zellij` is a newer, more modern terminal workspace and multiplexer, designed with a focus on good defaults and a more intuitive user experience.

**Pros:**
- Modern design and user interface.
- Sensible defaults that often require less configuration out of the box.
- Built-in layout management.
- Rust-based, often praised for performance and safety.

**Cons:**
- Newer, so the ecosystem of plugins and community support is smaller than `tmux`.
- May not have the sheer depth of customization options available in `tmux` (though this is also a pro for simplicity).

## Initial Thoughts / Direction

Given the preference for good defaults and minimal tinkering, `Zellij` is the stronger contender — modern take on multiplexing without the configuration overhead of `tmux`.

## Current status

Not using either. The setup cost hasn't been worth it yet — plain terminal, one thing per tab works fine for now.

The main argument for multiplexers is session persistence: if your connection drops or terminal closes, the session keeps running server-side. That matters most when SSHing into remote servers and running things interactively. That pattern is largely avoided here in favour of CI/CD pipelines — if something needs to run remotely, it runs in a pipeline, not in a terminal session.

Working locally with a modern terminal (iTerm2, Wezterm, etc.) that has native tabs and split panes, the marginal gain is genuinely small day-to-day. Rational laziness — the cost-benefit only flips when remote work or session persistence becomes a real part of the workflow.

Will revisit if that assumption changes.
