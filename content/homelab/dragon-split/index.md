---
title: "Dragon Split — Slicing a Model for Print"
description: "Taking an existing articulated dragon STL and splitting it into printable parts using Blender Python. A different class of problem: mesh manipulation rather than parametric generation."
date: 2026-06-02
draft: true
layout: single
showReadingTime: false
tags: ["blender", "python", "3d-printing", "mesh", "remixing"]
---

Source: [Articulated Dragon remixes on Thingiverse](https://www.thingiverse.com/thing:3297044/remixes)

The model is too large to print in one piece on most beds. The suggestion — from ChatGPT — was to split it into segments and print in parts. The framing was "suitable work for AI": find sensible cut planes, generate connectors or alignment pins at each split, keep the seams visually clean.

---

## Why this is a different class of problem

The rack brace and buckle start from nothing — the script *is* the geometry. This is the opposite: an existing mesh that needs to be cut up without understanding how it was made.

The challenges are different:

- **Cut planes**: where to slice so seams hide in natural breaks (joints, scales, underbelly)
- **Connectors**: pins, sockets, or keys at each face to align parts during glue-up
- **Non-manifold geometry**: downloaded STLs are often dirty — boolean cuts on bad meshes produce garbage
- **No parametric handle**: changing a cut requires re-running the whole split, not editing a config value

---

## Approach

*To be worked out.* Likely: import STL → clean mesh → define cut planes as empties or coordinates → boolean split per segment → add pin geometry at each face → export per-part STLs.

The question is how much of the cut-plane placement can be scripted versus needing manual viewport placement.

---

## Status

Not started. Notes to follow once the first cut attempt is done.

See also: [Rack Support Brace](/homelab/rack-support-brace/) — parametric baseline, different problem class.
