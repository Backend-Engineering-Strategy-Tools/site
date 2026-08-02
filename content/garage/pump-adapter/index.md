---
title: "Pump-to-Hose Adapter — Camping Fix"
description: "A Stromberg inflatable pillow and an Urberg sleeping mattress use incompatible valves. Designed and printed an adapter in Blender Python to bridge them, iterating through nine versions to get a self-supporting print and a lanyard tab that wouldn't snap off."
date: 2026-07-22
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric", "camping"]
---

Went camping. Brought a Stromberg inflatable pillow and an Urberg sleeping mattress — both use their own pump/bag-blow-up system, and the two valves don't match. Rather than blow up the pillow by mouth for a week, designed an adapter: one end presses into the mattress's 18mm hose fitting, the other slips over the pump's 23mm spigot.

Built in Blender Python — a solid of revolution, one closed (r, z) profile spun 360° with `bmesh.ops.spin`, no booleans for the base shape at all. Same approach as the [rack support brace](/homelab/rack-support-brace/) and other [procedural parts](/public-notes/frameworks-tools/blender-python/): geometry as a script, dimensions as a config block, not a modelling operation.

Two versions are worth keeping around; the rest of the iteration is compressed into the table below.

---

## Adapter — plain

No O-ring, no lanyard. Plug end (17.6mm OD, 0.4mm clearance) presses into the 18mm mattress hose fitting; socket end (23.3mm ID, 0.3mm clearance) slips over the pump's 23mm spigot. A tapered shoulder between the two — self-supporting on FDM, no support material needed.

{{< carousel images="code/procedural-mesh/pump-adapter/renders/adapter/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/pump-adapter/adapter.py" label="adapter.py" >}}
{{< download href="/code/procedural-mesh/pump-adapter/adapter.stl" label="adapter.stl" >}}

---

## Adapter — with tab

Same part, plus a lanyard tab on the socket wall so it can't wander off in the grass at a campsite — a small thing to lose forever if it's not tied to something. The tab took more iteration than the adapter itself: it's the one feature that isn't rotationally symmetric, and a load-bearing appendage fights back in ways a plain spun profile doesn't.

{{< carousel images="code/procedural-mesh/pump-adapter/renders/adapter-with-tab/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/pump-adapter/adapter_with_tab.py" label="adapter_with_tab.py" >}}
{{< download href="/code/procedural-mesh/pump-adapter/adapter_with_tab.stl" label="adapter_with_tab.stl" >}}

This is the version that actually went camping.

---

## Iteration

| Version                   | Change                                                                                                                                                                                                                                                  |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v1                        | First print. O-ring groove on the plug for sealing. Plug→socket shoulder was a sudden 90° step — printed as an unsupported ledge, came out rough.                                                                                                       |
| v2                        | Shoulder replaced with a taper shallow enough to self-support on FDM (≤45° off vertical).                                                                                                                                                               |
| v3 — **adapter**          | O-ring groove dropped entirely — v1's plain press fit sealed fine on its own, so the groove was pure margin. Plug shortened to match.                                                                                                                   |
| v4                        | Added a lanyard tab on the socket wall — the one non-rotationally-symmetric feature, needs its own small booleans.                                                                                                                                      |
| v5                        | v4's tab was a flat box on a flat bottom — an unsupported ledge, same mistake as v1's shoulder. Rebuilt as a rounded boss growing from an embedded apex.                                                                                                |
| v6                        | v5's lanyard holes were blind pockets that never broke through to open air — caught before printing. Replaced with a real horizontal through-hole, and a wider root since the tab is now load-bearing, not just a print-support concern.                |
| v7                        | Tab stuck up past the socket's rim and interfered with the pump housing. Simplified to a plain circle, one continuous taper, trimmed to clear the rim.                                                                                                  |
| v8                        | v7's tab still tapered down to a ~0.4mm root — fine for print angle, a snap point under real load. Rebuilt as a full second copy of the shoulder profile ("ear"), offset sideways and fused to the body along its whole height instead of at one point. |
| v9 — **adapter-with-tab** | v8's ear had a hidden flat-disc overhang at its own base (same class of bug as v1, in new geometry). Fixed by growing the offset itself from near-zero instead of holding it fixed, so the ear stays self-supporting the entire way up.                 |

---

## Print

PLA, Anycubic Kobra X, no O-ring — the press fit alone is tight enough to hold and seal.

---

## Photos

{{< figure src="/images/pump-adapter-printed.jpeg" caption="Adapter fresh off the printer." >}}

{{< figure src="/images/pump-adapter-tab-printed.jpeg" caption="Tab version — the one that actually went camping." >}}

{{< figure src="/images/pump-adapter-camping.jpeg" caption="In use at the campsite, bridging pump to mattress." >}}
