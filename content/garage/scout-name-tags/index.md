---
title: "Scout Gear Name Tags — Parametric, Multi-Material"
description: "A two-sided gear-shaped keyring tag — a castellated cog and a real fleur-de-lis on the front, 'Mölndal' + name (+ optional phone) on the back — parameterized by name in Blender Python and designed for genuine 4-color printing on the Kobra X's ACE Gen2 feeder. Short reference note, work in progress."
date: 2026-08-02
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric", "scout", "multi-color"]
---

Came home from a jamboree with an idea rather than a plan — another scout's kit had gear-shaped name tags, sharper than mine. Got sent the source `.3mf` for one. Credit to whoever designed the original — not naming them here without asking first, this page is my own remix for my own tags, not a republish of theirs.

Meant to be a quick "swap the name" edit. Turned into a from-scratch parametric rebuild once the source file turned out to be a baked, multi-part color-separated Bambu design (33 sub-parts, text embedded on the back face for a single-nozzle color-swap trick) — not worth reverse-engineering for a one-off edit.

This is a short reference note, not a finished writeup — the actual part still needs more work (no real print yet, everything below is renders). Useful as a starting point if you want to make more of these (future me) or generate your own name tag from a name.

Built in Blender Python, same pattern as the [rack support brace](/homelab/rack-support-brace/) and other [procedural parts](/public-notes/frameworks-tools/blender-python/): gear silhouette via `bmesh`, boolean ops for the hole and the recessed insert pockets.

**Parameterized by name (and optionally a phone number)** — the script takes CLI args and regenerates everything:

```
blender --background --python gear_name_tag.py -- "Manfred" "Nilsson"
blender --background --python gear_name_tag.py -- "Manfred" "Nilsson" "+46 70 000 00 00"
```

---

## Design

~42mm gear, keyring hole. Tooth count and profile aren't guessed — pulled from the actual Mölndals Scoutkår cog emblem by extracting the mesh from a reference `.3mf` and running an FFT over the radial (angle vs. radius) profile: 12 teeth, dominant harmonic magnitude ~3x the next candidate. The teeth are castellated/square — flat top, a straight *radial* step down to a flat root, not a diagonal ramp or a rounded scallop (both tried first, both wrong once checked against the reference image up close).

**Two full-thickness pieces, not one plate.** RING is the complete, unbroken gear solid — full teeth, full side walls, all red. WHITE_COG is the same tooth shape inset a couple mm in, with its own narrower, unbeveled teeth, sitting inside RING's footprint — reads as "a white cog inside the red cog" from the front, matching the reference emblem. A shallow (0.6mm) front-face-only version was tried first specifically to keep every side wall red, but it was too fragile to print and handle as its own piece — full thickness won, with the tradeoff that white's own tooth side-walls show at the inset boundary.

**Front**: cog + a real fleur-de-lis, not a font glyph. Traced from the actual [Mölndals Scoutkår](https://www.scouterna.se/) emblem image via marching-squares contour extraction (`skimage`) into a set of independent closed polygons, then extruded — a font's fleur-de-lis character (tried first, Apple Symbols `⚜`) doesn't look anything like the real emblem up close. The traced shape is 15 separate pieces (matching the source artwork's own disconnected curls); merging them into one blob first (via mask dilation) was tried and looked worse — smeared out all the fine swirl detail — so they're kept as independent islands in one insert instead.

**Back**: "MÖLNDAL", an optional phone number, and the name — three or four rows depending on whether a phone was given. The phone (when present) sits in the middle row, since the circle is widest there and the phone number is the longest string. Row pitch is uniform (6mm) across whatever rows are active. Text uses DIN Condensed Bold — the closest local match to the wordmark's bold, condensed look (including the dotted Ö), not the actual brand font.

**Keyring hole** sits in a tooth valley (not under a tooth tip — too little material there to be worth it), and is always the *last* boolean applied, after every recess. Cutting it earlier bit twice: once it silently vanished (a hole-shaped gap in a duplicated cutter left the surrounding piece solid instead of hollow), once it left a solid plug exactly where it should have been open. Same root cause both times — Blender's `EXACT` solver getting confused when a full-depth hole interacts with whatever boolean comes after it.

Six STL shells (five without a phone number), four filament colors: ring (red), white_cog (white), logo (blue), and molndal + firstname + surname (+ phone) sharing one black slot. Genuine multi-material printing (Kobra X + ACE Gen2, or any AMS-equivalent feeder) — no single-nozzle color-swap trick, unlike the source file this started from.

{{< download href="/code/procedural-mesh/scout-name-tags/gear_name_tag.py" label="gear_name_tag.py" >}}

## Example — Manfred Nilsson

{{< carousel images="code/procedural-mesh/scout-name-tags/renders/example_manfred_nilsson/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/ring.stl" label="ring.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/white_cog.stl" label="white_cog.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/logo.stl" label="logo.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/molndal.stl" label="molndal.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/firstname.stl" label="firstname.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/surname.stl" label="surname.stl" >}}

No phone number in this example (kept the public version free of a real one) — the script supports it, just pass a third argument. All six shells share the same coordinate space, so importing them together in a slicer aligns them automatically without needing a combined file.

---

## Lessons

| Issue | Fix |
|---|---|
| Cutting the keyring hole early (before other recesses) made it vanish, or later left a solid plug exactly where it should have been open — `EXACT` solver getting confused by a full-depth hole interacting with a later boolean, not consistent about which way it fails. | Cut the hole dead last, after every other boolean on that piece, full stop. |
| A shallow (0.6mm) front-face-only inset cog kept every side wall red, but was too fragile to print/handle as its own piece. | Went full-thickness instead, accepting that the inset cog's own tooth side-walls show at the boundary — a real design tradeoff, not a bug. |
| A font glyph (Apple Symbols `⚜`) for the fleur-de-lis didn't look like the actual emblem once compared side by side. | Traced the real logo image into polygons via marching-squares contour extraction (`skimage.measure.find_contours`) and extruded those instead. |
| Dilating the traced mask to merge 15 disconnected curl pieces into one printable blob smeared out all the fine swirl detail — looked much worse than the source. | Left the pieces as independent islands in one STL insert instead of forcing them into one connected shape. |
| Oversized, overlapping text recesses (all rows briefly set to the same size as the whole disc) corrupted the boolean result — back-face text leaked through to the front render. | Confirms non-overlapping cutter geometry matters for the `EXACT` solver, same class of issue as the hole-ordering bug — verify via an actual render, overlap isn't always obvious from the numbers alone. |
| Blender's `TRACK_TO` camera constraint with `up_axis='UP_Y'` produces a mirrored chirality specifically when the camera sits below the target looking up — confirmed by comparing against an explicit look-at matrix built with the same up vector. | Point cameras with a manual look-at matrix (cross products) instead of a constraint for any render angle that needs to be trustworthy for reading text. |

---

## Print

PLA, Anycubic Kobra X + ACE Gen2. Assign a filament per shell in Anycubic Slicer Next after importing all shells (Split to Objects / per-shell color assignment) — molndal, firstname, surname, and phone (if present) all get the same black filament.

---

## Photos

{{< figure src="/images/scout-name-tags-printed.jpeg" caption="Printed name tag, front and back." >}}
