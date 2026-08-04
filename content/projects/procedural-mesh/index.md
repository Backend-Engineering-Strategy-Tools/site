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
| 3 | Headless render — Blender 5.1.2 + Dagger pipeline; STL → multi-angle PNGs without opening Blender; smoke-tested and running in CI | Done |
| 4 | [Scout Buckle](/garage/scout-buckle/) — complex geometry; compound curves, functional tongue mechanism, tolerances that matter | In progress |
| 5 | CI/CD pipeline — STL or script change → GitHub Actions → Dagger → PNG artifacts; [procedural-mesh-pipeline](https://github.com/Backend-Engineering-Strategy-Tools/procedural-mesh-pipeline) | Done |
| 6 | AI feedback loop — describe correction → updated script → re-run, without opening Blender | Planned |
| 7 | [Dragon Split](/garage/dragon-split/) — mesh manipulation; cut an existing articulated dragon STL into printable segments with connectors | Not started |
| 8 | [Pump-to-Hose Adapter](/garage/pump-adapter/) — solid of revolution via `bmesh.ops.spin` instead of booleans; nine iterations chasing self-supporting FDM geometry and a load-bearing lanyard tab | Done |
| 9 | [Extrusion Feet](/garage/extrusion-feet/) — one script, single- and dual-track T-slot variants via a `TRACK_COUNT` switch; source of the bevel-after-boolean and manifold-vs-connected-solid gotchas on the [Blender Python](/public-notes/frameworks-tools/blender-python/) page | Done |

---

## Notes

The rack brace (step 2) was easier than expected — straightforward geometry, minimal iteration. That is why the pipeline steps did not get built yet: the manual workflow was fast enough that the overhead of automating it was not justified for one part.

The scout buckle (step 4) is the harder test. Compound curves and functional constraints mean the script has needed partial rebuilds rather than config-block edits. That is the case that justified building the render pipeline properly.

Steps 3 and 5 ended up built together rather than sequentially. The pipeline lives in a separate repo — [procedural-mesh-pipeline](https://github.com/Backend-Engineering-Strategy-Tools/procedural-mesh-pipeline) — Dagger + GitHub Actions, Blender 5.1.2 headless, Cycles CPU. Renders run natively on the CI runner (amd64); locally the pipeline is used for smoke-testing the image only. Blender has no official ARM64 Linux binary so local renders under emulation are impractical.

The dragon split (step 7) is a different class of problem — remixing rather than generating. Worth keeping in the same project because the tooling overlaps (Blender Python, STL export) even if the approach does not.

The pump adapter (step 8) introduced a third generation technique alongside booleans: a solid of revolution, spinning one closed (r, z) profile 360° with `bmesh.ops.spin`. No booleans in the base shape at all — a better fit for rotationally symmetric parts than the plate-and-holes approach used through step 4.

The extrusion feet (step 9) went back to booleans, and turned into the most expensive debugging session of the family so far — the actual design took a few rounds of user feedback (T-slot key profile, box stacking order), but a plain-looking rounded box hid two separate silent-corruption bugs (bevel-post-boolean, and a near-zero gap masquerading as a valid union) that both passed manifold and bounding-box checks and were only caught by rendering. Worth the detour: the render-camera fixes and the "manifold isn't the same as one connected solid" lesson both apply to every future step in this family, not just this one part.
