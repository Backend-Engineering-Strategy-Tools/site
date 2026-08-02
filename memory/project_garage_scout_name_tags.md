---
name: garage scout name tags
description: Status of the Scout Gear Name Tags garage page and related lessons-learned additions (all uncommitted)
type: project
---

Added 2026-08-02, working tree only — nothing committed or pushed.

**New page:** `content/garage/scout-name-tags/` (`draft: true`). Parametric gear-shaped keyring tag built in Blender Python — fleur-de-lis + "Mölndal" + first/last name, recessed inserts for genuine multi-material printing (Kobra X + ACE Gen2). Script + example output (Manfred Nilsson only — other names stripped for privacy) live at `assets/code/procedural-mesh/scout-name-tags/`.

**Still TODO on that page** (explicitly stubbed, not forgotten):
- Full writeup of the reverse-engineering dead-end — the source `.3mf` turned out to be a baked, multi-part color-separated Bambu design (33 sub-parts, text embedded on the back face for a single-nozzle color-swap trick), not worth salvaging for what was meant to be a one-off text edit.
- Photos.
- Flip `draft: true` → `false` once the above is done.
- Possible follow-up: swap the hand-approximated fleur-de-lis (Apple Symbols.ttf glyph, voxel-remeshed) for the existing proper asset at `assets/code/mesh/scout_emblem/scout_emblem.stl`.

**Lessons-learned additions to `content/public-notes/frameworks-tools/blender-python/index.md`** (extends its existing `Limitations` section and `STL export` subsection — this is the established home for cross-project Blender/3D-printing gotchas, not a separate page):
- Non-manifold font/glyph-derived boolean cutters silently corrupting the `EXACT` solver (fix: voxel remesh before the boolean).
- Multi-part STL export needs to be one combined file — slicers auto-center each independently-imported STL, breaking relative alignment.
- Recessed-insert pattern for genuine multi-material printing (AMS/ACE-Gen2-style feeders).

**`content/garage/3d-printing.md`**: the "Slicer / Workflow" section (previously just a TODO placeholder) is now filled in with the ACE Gen2 multi-color workflow and a link back to the blender-python notes page.

**Also sitting uncommitted** (pre-existing, unrelated to this work, not touched): `content/garage/pump-adapter/` + its assets — a finished (`draft: false`) page, just never committed.
