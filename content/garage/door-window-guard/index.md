---
title: "Door & Window Guard — Bud"
description: "Printing a door guard and window guard for my nephew, from two MakerWorld models that look like the same design family — the body on both needed elongating to actually fit, via a cut/donor/splice STL-surgery pass in Blender."
date: 2026-08-12
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric"]
---

Printing a door guard and window guard for my nephew. Found two models on MakerWorld that look like the same "Bud" design family, going by the naming — [Door Guard Bud](https://makerworld.com/en/models/3100132-door-guard-bud?from=search#profileId-3494300) and [Window Guard Bud](https://makerworld.com/en/models/3031886-window-guard-bud#profileId-3414696), both by [Patrick (@Pattemanden)](https://makerworld.com/en/@Pattemanden) — assuming they're compatible with each other since they're the same maker, not yet confirmed.

{{< figure src="/images/door-window-guard-render.png" caption="Design comparison — tan is the as-found original, blue is the elongated version, ruler squares are 10mm. Left pair: door body. Right pair: window body." >}}

{{< figure src="/images/door-window-guard-photo.png" caption="Printed parts. Top: the door's pivot-bolt head assembly. Middle (tapered edge): door body, extended. Bottom (straight): window body, extended. Ruler in cm." >}}

---

## Status

Printed both as found. The body on both needs elongating to actually fit — solved with a cut/donor/splice STL-surgery pass in Blender rather than a uniform scale: cut the body, keep both ends fixed-size, extend the gap between them with a stretched donor slice taken from a constant-cross-section region. Keeps every real feature (corners, slots, snap-fits) at original size — only the boring middle grows.

Both bodies also have screw holes and other features to route around — the donor slice needs a genuinely hole-free "safe zone" to stretch from, and the elongation needs to leave the screw holes at sane positions relative to the mounting surface afterward.

**Door body done.** `obj_1_doorbed14deg.stl` is a hook/cleat bracket, not a pair of legs: a tapered foot tip, a flat inner face the door karm actually rests against (constant width the whole way, 20mm thick throughout, that's the "80mm" opening), then a block carrying the pivot-bolt hole for `obj_2_newhead` (locked with the separate printed `obj_3_largebolt` / `obj_5_shortBolt` — not touched). The outer edge is a dead-straight 14° taper (matches the `14deg` filename) the whole run.

Took seven attempts to get right. The shaft has its own main screw hole/mounting slot (~14mm wide, running most of the flat span but *not* all the way to the tip) — separate from a second, genuine screw hole. First few attempts assumed the far block (with the visible round hole) was one simple piece; it isn't. It's two things stacked: a plain continuation of the shaft's own taper+slot sitting *above* Y=145.77 (the shaft's own constant edge), and a completely separate flange/pedestal — the actual bolt-hole housing — sitting below that line. Confirmed by bisecting through the block: two distinct internal holes there, cleanly split by that Y value, never overlapping.

1–3. **Donor-slice-stretch, then rigid-translate-the-block + connector (solid, then hollow tapered)** — all treated the far block as one indivisible piece and either stretched, plugged, or approximated through the main slot. Each failed once actually inspected: a kinked hole, a phantom wall visible when sliced, or "no clean slice to extend" — the slot runs through virtually the whole span, so any interpolation was approximating a hole with no representative reference points.
4. **Cut at the far block's natural joint, non-tapered box extension** — technically clean but the wrong end — cut off and moved the whole far block, when only its lower flange needed to move.
5. **Cut the near foot tip instead** — clean but still the wrong piece: neither end actually isolates just the bolt hole.

At this point it wasn't clear anymore whether the disagreement with Claude (doing the actual Blender work here) was about the geometry or just about words. Five rounds of "cut the leg off, move it" back and forth hadn't converged, so I asked it directly how to explain this better. What actually broke the stall: it rendered the part with the sub-regions color-coded (foot tip / shaft / far block) and the axis gizmo labeled red/green/blue — the same colors it had already been using in every render up to that point, so nothing new to learn mid-argument, just a reference we could both already read. My next message used those same color labels straight back ("cut perpendicular to green, main body = grey part"), and the actual structure — a compound feature it had been treating as one piece — came out in a single exchange after five rounds of prose hadn't gotten there. Worth remembering next time something spatial gets stuck in translation with an LLM: stop describing, start pointing at something labeled.

6. **Split the far block along Y first** — separate the bolt-hole flange (Y<145.77) from the block's plain upper continuation (Y≥145.77) before touching anything else, then extend the now hole-free-in-that-span shaft with the same box-CSG technique. Closer, but the extension point (right where the block starts) still had the main slot passing through it, needing a hollow (outer-minus-slot) box — some residual non-manifold edges at that seam.
7. **Move the extension point further out** — the actual fix. The main slot doesn't run to the very tip: bisecting in 0.1mm steps found it closes off completely between x=173.9 and 174.0, leaving the last ~7mm before the tip (once the bolt-hole flange is set aside) completely solid — no slot, no hole, nothing. Extending there instead means a plain **solid** box, nothing to subtract, nothing left to get subtly wrong. The bolt-hole flange still gets separated (as in attempt 6) and cut at its own natural boundary further back, independent of where the body extension happens.

+40mm extension → opening goes from 82mm to 122mm, inside the 110-130mm target. Output: `obj_1_doorbed14deg_extended.stl` — 1 connected component, 25 residual non-manifold edges out of ~15,000 faces (trivial, at the two extension seams). Verified: cross-section scan across the whole new span shows the main slot present in the shaft, a genuinely solid zone through the extension (no internal loops at all), then the bolt hole reappearing correctly where the reattached flange sits — exactly the intended structure. Silhouette has no phantom geometry. `EXTENSION`/`LEG_CUT_X`/`BODY_CUT_X`/`CUT_Y` are the main knobs if the target length needs adjusting.

{{< download href="/code/procedural-mesh/door-window-guard/extend_doorbed.py" label="extend_doorbed.py" >}}
{{< download href="/code/procedural-mesh/door-window-guard/obj_1_doorbed14deg_extended.stl" label="obj_1_doorbed14deg_extended.stl" >}}

Passed visual review this time.

**Window body — done, 2026-08-13, first attempt.** `obj_1_window_bud.stl` turned out much simpler to read than the door: three clean, non-overlapping zones along its length, no stacked features to untangle. A near-end mounting block (full 50mm width, carries the wall screw hole) stays fixed. A genuinely hole-free, constant-cross-section zone follows it (confirmed empty by a 0.2mm-step scan on both edges) — the safe cut zone. Past that, one long zone runs to the tip: an internal slot with a wavy profile (a spring/latch channel for the bolt-lock) plus a stepped notch right at the end. Confirmed by a color-coded render (same convention as the door session) that this whole tip zone is one piece, not two stacked features the way the door's far block was — so it just needed to translate outward as a rigid block, nothing internal to reslice.

Since the frame thickness is the same for both parts, the target gap is the same too — reused the door's +40mm. Cut once inside the safe zone, kept the near side fixed, translated the tip side (lock mechanism included) by +40mm, bridged with a plain solid box (no void to subtract, since that zone has no holes at all). No leg/flange separation step needed, unlike the door. Result: opening 139.83mm → 179.83mm. 1 connected component, 46 residual non-manifold edges out of ~14,600 faces (trivial, at the two extension seams). Verified by cross-section scan across the whole new span: hole-free through the entire extension, then the lock mechanism's slot and stepped notch reappear exactly as in the original, shifted by the full 40mm.

{{< download href="/code/procedural-mesh/door-window-guard/extend_window.py" label="extend_window.py" >}}
{{< download href="/code/procedural-mesh/door-window-guard/obj_1_window_bud_extended.stl" label="obj_1_window_bud_extended.stl" >}}

