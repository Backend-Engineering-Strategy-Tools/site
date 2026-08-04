---
title: "Extrusion Feet — 2020 / 2040 T-Slot"
description: "Parametric raised feet for 20-series T-slot aluminium extrusion, single-track and dual-track, designed in Blender Python to stand the laser cutter frame off the bench."
date: 2026-08-04
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric", "laser-cutter"]
---

Needed feet for the [laser cutter build](/garage/laser-cutter/) — its frame sits on 20-series T-slot extrusion, bare aluminum straight on the bench. Small enough on its own to be its own quick write-up.

Built as a parametric pair in Blender Python instead: one script, one `TRACK_COUNT` switch between a single- and a dual-track version.

{{< download href="/code/procedural-mesh/extrusion-feet/foot.py" label="foot.py" >}}

---

## Spec

Both versions share the same T-slot key: a narrow stem (5.8mm) through the slot's 6mm mouth, widening to a 7.6mm head captured inside the 8mm channel — installed like a normal T-nut, slid in from the open end of the extrusion rather than pressed in from below. A central M5 clearance hole takes a bolt up into a T-nut in the channel.

- **Single-track (2020)** — one key, 24×40mm base, 28×44mm shoulder.
- **Dual-track (2040)** — two keys 20mm apart (standard 20-series module pitch), 36×40mm base, 40×44mm shoulder.

## Single-track (2020)

{{< carousel images="code/procedural-mesh/extrusion-feet/renders_single_track/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/extrusion-feet/foot_single_track.stl" label="foot_single_track.stl" >}}

## Dual-track (2040)

{{< carousel images="code/procedural-mesh/extrusion-feet/renders_dual_track/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/extrusion-feet/foot_dual_track.stl" label="foot_dual_track.stl" >}}

---

## Photos

{{< figure src="/images/extrusion-feet-printed.jpeg" caption="Printed foot, single-track version, under the laser cutter frame." >}}
