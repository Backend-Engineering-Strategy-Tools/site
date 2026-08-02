---
title: "Scout Gear Name Tags — Parametric, Multi-Material"
description: "A two-sided gear-shaped keyring tag — a castellated cog and a real fleur-de-lis on the front, 'Mölndal' + name (+ optional phone) on the back — parameterized by name in Blender Python and designed for genuine 4-color printing on the Kobra X's ACE Gen2 feeder. Short reference note, work in progress."
date: 2026-08-02
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric", "scout", "multi-color"]
---

Came home from a jamboree with an idea rather than a plan — another scout's kit had gear-shaped name tags, sharper than mine. Credit where credit's due to whoever designed the original — this page is my own remix for my own tags, not a republish of theirs.

Meant to be a quick "swap the name" edit, turned into a from-scratch parametric rebuild.

This is a short reference note. Useful as a starting point if you want to make more of these (future me) or generate your own name tag from a name.

Built in Blender Python, same pattern as the [rack support brace](/homelab/rack-support-brace/) and other [procedural parts](/public-notes/frameworks-tools/blender-python/): gear silhouette via `bmesh`, boolean ops for the hole and the recessed insert pockets. See that page for the boolean-ordering, non-manifold-cutter, FFT-profile, and logo-tracing gotchas this build ran into.

**Parameterized by name (and optionally a phone number)** — the script takes CLI args and regenerates everything:

```
blender --background --python gear_name_tag.py -- "Manfred" "Nilsson"
blender --background --python gear_name_tag.py -- "Manfred" "Nilsson" "+46 70 000 00 00"
```

---

## Design

~42mm gear, keyring hole. Tooth count and profile aren't guessed — pulled from the actual Mölndals Scoutkår cog emblem by extracting the mesh from a reference `.3mf` and running an FFT over the radial (angle vs. radius) profile: 12 teeth, dominant harmonic magnitude ~3x the next candidate. The teeth are castellated/square — flat top, a straight *radial* step down to a flat root, not a diagonal ramp or a rounded scallop.

**Two full-thickness pieces, not one plate.** RING is the complete, unbroken gear solid — full teeth, full side walls, all red. WHITE_COG is the same tooth shape inset a couple mm in, with its own narrower, unbeveled teeth, sitting inside RING's footprint — reads as "a white cog inside the red cog" from the front, matching the reference emblem.

**Front**: cog + a real fleur-de-lis, not a font glyph. Traced from the actual [Mölndals Scoutkår](https://www.scouterna.se/) emblem image via marching-squares contour extraction (`skimage`) into a set of independent closed polygons, then extruded. The traced shape is 15 separate pieces (matching the source artwork's own disconnected curls).

**Back**: "MÖLNDAL", an optional phone number, and the name — three or four rows depending on whether a phone was given. The phone (when present) sits in the middle row, since the circle is widest there and the phone number is the longest string. Row pitch is uniform (6mm) across whatever rows are active. Text uses DIN Condensed Bold — the closest local match to the wordmark's bold, condensed look (including the dotted Ö), not the actual brand font.

**Keyring hole** sits in a tooth valley (not under a tooth tip — too little material there to be worth it), and is always the *last* boolean applied, after every recess.

Six STL shells (five without a phone number), four filament colors: ring (red), white_cog (white), logo (blue), and molndal + firstname + surname (+ phone) sharing one black slot. Genuine multi-material printing (Kobra X + ACE Gen2, or any AMS-equivalent feeder).

{{< download href="/code/procedural-mesh/scout-name-tags/gear_name_tag.py" label="gear_name_tag.py" >}}

## Example — Manfred Nilsson

{{< carousel images="code/procedural-mesh/scout-name-tags/renders/example_manfred_nilsson/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/ring.stl" label="ring.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/white_cog.stl" label="white_cog.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/logo.stl" label="logo.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/molndal.stl" label="molndal.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/firstname.stl" label="firstname.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/surname.stl" label="surname.stl" >}}
{{< download href="/code/procedural-mesh/scout-name-tags/example_manfred_nilsson/combined.3mf" label="combined.3mf" >}} — all six parts pre-colored in one file (red/white/blue/black), no manual per-shell color assignment needed

No phone number in this example (kept the public version free of a real one) — the script supports it, just pass a third argument. All six shells share the same coordinate space, so importing the separate STLs together in a slicer aligns them automatically without needing a combined file — the 3MF is there for convenience, not alignment.

---

## Print

PLA, Anycubic Kobra X + ACE Gen2. Import the `.3mf` and each part already carries its own color — just map each to a filament slot; molndal, firstname, surname, and phone (if present) all get the same black filament. Importing the separate STLs instead works too, just needs manual per-shell color assignment (Split to Objects) since STL carries no color data at all.

The whole assembly is built logo-side up, then flipped so it prints logo-down, text-up, flat, no supports — the visible front face ends up flush against the bed for a crisp finish.

---

## Photos

{{< figure src="/images/scout-name-tags-printed.jpeg" caption="Printed name tag, front and back." >}}
