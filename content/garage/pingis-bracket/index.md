---
title: "Ping-Pong Ball-Catch Net Mount"
description: "Rail-clamping bracket and plywood spacers for mounting a ball-catch net behind a ping-pong training robot — parametric, built in Blender Python."
date: 2026-08-06
draft: false
layout: single
showReadingTime: false
tags: ["3d-printing", "blender", "python", "parametric"]
---

A ball-catch net for a ping-pong training robot needs to mount at the table's end. The table has two wooden rails running under the apron edge — a bracket clamps onto each one and gives a flat face to screw a plywood board to, which carries the net.

---

## Rail bracket

Slides onto the rail lengthwise and hard-stops at a fixed position. Rail profile (neck, flare, 45° shoulder, rounded corners). Board attaches with wood screws driven straight into the print.

{{< carousel images="code/procedural-mesh/pingis-bracket/renders_pingis_bracket/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/pingis-bracket/bracket.py" label="bracket.py" >}}
{{< download href="/code/procedural-mesh/pingis-bracket/pingis_bracket.stl" label="pingis_bracket.stl" >}}

A `TEST_PIECE` flag in the script swaps in a 10mm slice of just the channel — open both ends, for a fast fit-check print before committing to the full part.

{{< download href="/code/procedural-mesh/pingis-bracket/pingis_bracket_test.stl" label="pingis_bracket_test.stl" >}}

---

## Spacers

Four plain spacer blocks that sit between the plywood sheets, holding them a fixed distance apart under compression.

{{< carousel images="code/procedural-mesh/pingis-spacer/renders/*" interval="2800" >}}

{{< download href="/code/procedural-mesh/pingis-spacer/spacer.py" label="spacer.py" >}}
{{< download href="/code/procedural-mesh/pingis-spacer/pingis_spacer.stl" label="pingis_spacer.stl" >}}
