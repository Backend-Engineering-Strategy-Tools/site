---
title: "Touchscreen HUD Build"
date: 2026-03-16
draft: false
showReadingTime: false
layout: single
---

A small batch of fanless Atom-based machines with touchscreens — picked up as a hardware experiment, now being packaged up to hand out to colleagues at nerd night.

The goal: a fully reproducible setup. Boot from a Debian preseed image, drivers configured, sensible defaults in place, and a demo running out of the box. Each machine goes out with a link back to the repo so anyone who wants to dig in or rebuild from scratch can do so.

**Repos**

- [touchdemo](https://github.com/Backend-Engineering-Strategy-Tools/touchdemo) — demo application running on the devices *(work in progress)*
- [debian-preseed-demo](https://github.com/Backend-Engineering-Strategy-Tools/debian-preseed-demo) — automated Debian install via preseed *(in progress)*

**Still to figure out**

- Power adapter specs and sourcing
- Preseed configuration — touch input, display drivers, auto-login
- First-boot experience and documentation
