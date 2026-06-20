---
title: "Beehive Frame Spacer Clips"
date: 2026-06-20
draft: false
showReadingTime: false
tags: ["3d-printing", "blender", "beekeeping", "parametric"]
---

Father-in-law keeps bees. Each hive frame needs a small clip on the top bar that pushes adjacent frames apart and holds the correct 6 mm bee space between them. Wrote a Blender Python script to generate it.

C-shaped snap-on clip — straddles the bar from above, two arms hang down and grip the sides. The right arm protrudes 6 mm: when neighbouring frames each carry a clip the bumps press against each other and lock the spacing. Flat rectangular teeth on each arm inner face keep it from sliding off.

| Version | Changes | Script | STL |
|---------|---------|--------|-----|
| v1 | Side-mount. Clips onto bar edge horizontally. Single ramp barb. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v1.py" label="beehive_clip_v1.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_001.stl" label="clip_001.stl" >}} |
| v2 | Redesigned top-mount — straddles bar from above. Short arms (8 mm), thin bridge. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v2.py" label="beehive_clip_v2.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_002.stl" label="clip_002.stl" >}} |
| v3 | Stiffer bridge (3 mm), longer arms (14 mm), barb moves deeper. Inscriptions added. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v3.py" label="beehive_clip_v3.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_003.stl" label="clip_003.stl" >}} |
| v4 | Flat/rectangular teeth — equal resistance on push and pull. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v4.py" label="beehive_clip_v4.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_004.stl" label="clip_004.stl" >}} |
| v5 | Three ramp teeth per arm (8.5/12/15.5 mm). Arms extended to 17.5 mm. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v5.py" label="beehive_clip_v5.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_005.stl" label="clip_005.stl" >}} |
| v6 | Back to single ramp barb, bigger bite (4 mm). Arms to 18 mm. Spacer reduced to 4 mm. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v6.py" label="beehive_clip_v6.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_006.stl" label="clip_006.stl" >}} |
| v7 | Flat teeth again (v4 style), bite 6 mm. | {{< download href="/code/procedural-mesh/beehive-clip/beehive_clip_v7.py" label="beehive_clip_v7.py" >}} | {{< download href="/code/procedural-mesh/beehive-clip/clip_007.stl" label="clip_007.stl" >}} |
