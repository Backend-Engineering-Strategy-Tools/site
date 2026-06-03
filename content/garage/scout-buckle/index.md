---
title: "Scout Buckle Clone — Parametric for Casting"
description: "Reverse-engineering a Scout buckle in Blender Python for resin or metal casting. An iterative project that resists one-shotting — geometry with compound curves and tight tolerances."
date: 2026-06-02
draft: false
layout: single
showReadingTime: false
tags: ["blender", "python", "3d-printing", "parametric", "casting"]
---

Clone of a Scout buckle — built in Blender Python for casting rather than FDM printing. The goal is a dimensionally accurate reproduction suitable for resin or lost-wax casting.

What makes this different from the rack brace: the buckle geometry is not a simple boolean grid. It has compound curves, a tongue mechanism, and tolerances that matter for function. One-shotting it in Python is harder — the script has gone through multiple partial rebuilds rather than a single config-block iteration.

---

## Scripts

{{< download href="/code/procedural-mesh/buckle/buckle_v1.py" label="buckle_v1.py" >}}
{{< download href="/code/procedural-mesh/buckle/buckle_part1.py" label="buckle_part1.py" >}}
{{< download href="/code/procedural-mesh/buckle/buckle_part2_v1.py" label="buckle_part2_v1.py" >}}
{{< download href="/code/procedural-mesh/buckle/buckle_part2_v2.py" label="buckle_part2_v2.py" >}}

The split into `part1` / `part2` reflects the geometry breakdown — building the frame and the tongue separately before joining, which turned out to be easier to iterate on than a single monolithic script.

---

## What the iteration looks like

*Notes to follow.* The short version: parametric geometry that has functional constraints (a tongue that must seat and release under load) fights back more than decorative geometry. Changing one dimension propagates into several others in ways that aren't obvious from a config block alone.

---

## Casting considerations

*Notes to follow.* Draft angles, wall thickness minimums, and sprue placement are constraints that don't exist in FDM — the script needs to know about them.

---

## Status

Work in progress. Geometry is close; casting prep not started.

See also: [Rack Support Brace](/homelab/rack-support-brace/) — simpler parametric baseline using the same approach.
