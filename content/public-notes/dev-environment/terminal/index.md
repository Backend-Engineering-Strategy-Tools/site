---
title: "Terminal Setup Notes (macOS): Kitty → Ghostty Exploration"
date: 2026-05-06
draft: false
tags: ["terminal", "macos", "cli", "tools"]
showReadingTime: false
layout: single
---

I've been using **kitty** as my main terminal for a while. It's fast, stable, and very capable — but I've realized I don't actually enjoy tweaking terminal configs or maintaining a highly customized setup.

So I'm exploring simpler alternatives with good defaults.

---

## Current direction: Ghostty

Trying out: **Ghostty**  
https://ghostty.org/

Why:

- Clean macOS-native feel
- GPU-accelerated and fast
- Tabs + splits built in
- Designed for sane defaults (low configuration overhead)
- Keyboard-first workflow works well out of the box
- **My only config change:** Remapped tab switching shortcut (default `][` to `alt-[/]` for easier access on a Swedish keyboard layout).

Goal:  
Less time configuring terminal → more time working.

---

## Why the switch

- **Simplified setup:** I found myself spending less time tweaking and more time working.
- **Perceived responsiveness:** Both are fast, but Ghostty felt marginally snappier in heavy-usage scenarios.
- **Clean design:** The aesthetic and functional minimalism resonated more with my current preferences.

---

## What I'm moving away from (for now)

## kitty
https://sw.kovidgoyal.net/kitty/

What I liked:
- Very fast, GPU-accelerated rendering
- Highly configurable via a single `kitty.conf`
- Excellent font rendering — ligatures, custom fonts
- Extensible with Kitten modules (tabs, scrollback, multiplexing)
- Stable and mature

Why I'm moving on:
- Too much customization surface area
- I don't actually enjoy tuning it

---

## Other tools I've looked at

## Warp

https://warp.dev/

Warp feels like a "terminal reinvented" (more IDE-like, block-based UI, AI features). It's interesting, but feels a bit too opinionated and visually heavy for my taste.

---

## Other Terminal Emulators (briefly noted)

While Kitty and Ghostty are modern GPU-accelerated terminals, it's worth acknowledging other terminal emulators that have been foundational or offer different philosophies.

### xterm (and related TTYs)
https://www.x.org/releases/X11R7.6/doc/man/man1/xterm.1.xhtml

The classic X Window System terminal emulator. While not as feature-rich or graphically advanced as modern options, `xterm` (and its derivatives like `urxvt`, `st`, etc.) represent the minimalist, highly customizable end of the spectrum. They often prioritize resource efficiency and adherence to traditional Unix principles. Good for when you need something simple and rock-solid, but usually requires more effort to get a pleasant default experience.

---

## Current philosophy

I'm optimizing for:

- minimal clutter
- fast keyboard workflow
- good defaults (not deep config systems)
- fewer moving parts

---

## Current setup direction

- Terminal: **Ghostty**
- Tabs: built-in (no extra tooling yet)
- Multiplexing: not using tmux/Zellij for now
- Keeping things intentionally simple

---

## Open question

If Ghostty tabs feel too minimal in real use, I may revisit:

- Zellij (for structured sessions)
- tmux (unlikely unless necessary)

For now, keeping it simple on purpose.
