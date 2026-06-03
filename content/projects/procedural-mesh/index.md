---
title: "Procedural Mesh — Blender Python & AI-Assisted Geometry"
date: 2026-06-02
draft: false
layout: single
showReadingTime: false
tags: ["blender", "python", "3d-printing", "parametric"]
---

Using Python scripts inside Blender to generate, manipulate, and export geometry — rather than modelling by hand. The config block is the model. Changing a dimension means editing a constant and re-running, not touching a mesh.

Two related but distinct approaches:

- **Parametric generation** — the script builds geometry from scratch. Holes, plates, text engravings, export to STL, automated renders. The shape lives entirely in code.
- **Mesh manipulation** — an existing STL is imported and cut up. Different problem: no parametric handle, working with whatever the downloaded mesh gives you.

Both involve AI in the loop — either iterating on the Python with Claude, or using AI to determine cut planes on existing geometry.

---

## Stages

| Step | | Status |
|------|-|--------|
| 0 | Manual Blender modelling — [Packat & Klart badge](/garage/scout-badges-resin/) and [scout emblem casting master](/garage/casting-badges/); learning the tool before scripting | Done |
| 1 | [Approach documented](/public-notes/frameworks-tools/blender-python/) — Python scripted geometry, config-block iteration pattern | Done |
| 2 | [Rack Support Brace](/homelab/rack-support-brace/) — first implementation; flat plate, boolean hole grid, engraved text, automated renders | Done |
| 3 | Headless render — run existing `.blend` files (badge, emblem, brace) from terminal without GUI; prove the pipeline before writing new geometry | Next |
| 4 | [Scout Buckle](/garage/scout-buckle/) — complex geometry; compound curves, functional tongue mechanism, tolerances that matter | In progress |
| 5 | CI/CD pipeline — parameter change → headless render → PNG artifacts in PR | Planned |
| 6 | AI feedback loop — describe correction → updated script → re-run, without opening Blender | Planned |
| 7 | [Dragon Split](/garage/dragon-split/) — mesh manipulation; cut an existing articulated dragon STL into printable segments with connectors | Not started |

---

## Notes

The rack brace (step 2) was easier than expected — straightforward geometry, minimal iteration. That is why the pipeline steps did not get built yet: the manual workflow was fast enough that the overhead of automating it was not justified for one part.

The scout buckle (step 4) is the harder test. Compound curves and functional constraints mean the script has needed partial rebuilds rather than config-block edits. That is where the headless render pipeline (step 3 → 5) will actually pay off.

The dragon split (step 7) is a different class of problem — remixing rather than generating. Worth keeping in the same project because the tooling overlaps (Blender Python, STL export) even if the approach does not.
