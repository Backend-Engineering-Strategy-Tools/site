---
title: "Scout Scarf Slide — Parametric Woggle"
description: "A gear-shaped medallion (same cog + fleur-de-lis as the name tags) fused to a wider nameplate with a half-pipe loop for the rolled neckerchief — parameterized by name in Blender Python."
date: 2026-08-02
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric", "scout", "multi-color"]
---

Sibling of the [gear name tags](/garage/scout-name-tags/) — same front medallion (cog + fleur-de-lis), copied into its own project because the back is a completely different mechanism: a scout neckerchief slide (woggle) instead of a keyring tag. No hole, no back-face text on the medallion itself; instead a half-pipe loop holds the rolled scarf, and a wider white nameplate carries the name.

**Parameterized by name** — the script takes one CLI arg and regenerates everything:

```
blender --background --python scarf_slide.py -- "Manfred"
```

---

## Design

**Front**: unchanged from the name tags — the same 12-tooth castellated cog with a white inset cog and the traced fleur-de-lis stamp. See [that page](/garage/scout-name-tags/) for how those were derived.

**Back**: no text on the medallion at all. Instead:

- A **gear-shaped slot** cut clean through the nameplate, sized to the medallion's own outline plus a little clearance — the medallion is a separate print that inserts into it like a puzzle piece rather than gluing two flat plates face-to-face. Same thickness on both, so the joint sits flush on both sides.
- A **half-pipe loop**, its own black STL (not fused to the sign — it needs its own filament), sitting flush against the nameplate's back, clear of the slot, holding a rolled/folded neckerchief.
- A **white nameplate** (40×40mm) — narrower than the medallion's own diameter (deliberately overlapping it by half the plate's height), the name recessed into the same front face the logo sits on, so both read the right way round from the same side.

Both pieces print face-down with no supports — the logo and the name each sit on their piece's local top face, so the final flip puts the visible surface flush against the bed for a crisp finish, with the loop left standing clear on the back.

Same Blender-Python pattern as the [name tags](/garage/scout-name-tags/) and the rest of the [procedural parts](/public-notes/frameworks-tools/blender-python/) — see that page for the boolean-ordering, camera, and mirroring gotchas this build ran into.

{{< download href="/code/procedural-mesh/scout-scarf-slide/scarf_slide.py" label="scarf_slide.py" >}}

## Example — Manfred

{{< carousel images="code/procedural-mesh/scout-scarf-slide/renders/example_manfred/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/ring.stl" label="ring.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/white_cog.stl" label="white_cog.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/logo.stl" label="logo.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/sign.stl" label="sign.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/name.stl" label="name.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/pipe.stl" label="pipe.stl" >}}
{{< download href="/code/procedural-mesh/scout-scarf-slide/example_manfred/combined.3mf" label="combined.3mf" >}} — all six parts pre-colored in one file (red/white/blue/black), no manual per-shell color assignment needed

---

## Photos

{{< figure src="/images/scarf-slide-printed.jpeg" caption="Printed scarf slide, front and back." >}}
