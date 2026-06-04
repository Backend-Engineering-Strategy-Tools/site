---
title: "3D Printing"
date: 2026-04-12
draft: false
showReadingTime: false
tags: ["3d-printing", "fdm", "resin", "hardware"]
---

Two printers: an FDM machine for structural and functional parts, a resin printer for detail work. Different tools for different jobs — the resin produces sharper geometry at the cost of more process overhead.

---

## FDM — Anycubic Kobra X

Current machine. Workhorse for rack accessories, enclosures, and anything that needs to be durable and dimensionally accurate. Printing in PLA for most jobs.

Replaced an older Prusa i3 MK0 that still works but is no longer the daily driver. Shelved for now. CNC conversion or rebuild is somewhere on the list, parts donor if it comes to that first.

|                |                                                    |
|----------------|----------------------------------------------------|
| Build volume   | 260 × 260 × 260 mm                                 |
| Bed            | PEI spring steel, max 100°C                        |
| Nozzle (stock) | 0.4 mm hardened steel, max 300°C                   |
| Speed          | 300 mm/s recommended, 600 mm/s max                 |
| Extrusion      | Direct drive                                       |
| Leveling       | LeviQ3.0 auto-leveling                             |
| Multicolor     | 4-colour native (ACE 2 Pro), expandable to 19      |
| Extras         | AI spaghetti detection, HD camera, filament runout |

**Nozzles on hand**: 0.4 mm (stock), 0.25 mm (not tried yet). Expandable to 0.6 / 0.8 mm.

**Filament on hand**

| Brand     | Material  | Colour          | Qty     | Notes                                   |
|-----------|-----------|-----------------|---------|-----------------------------------------|
| Verbatim  | PLA       | Black           | 1 kg    | Original stock                          |
| Bambu Lab | PLA Basic | Orange          | 1 kg    |                                         |
| Bambu Lab | PLA Basic | Green           | 1 kg    |                                         |
| Bambu Lab | PLA Basic | Magenta         | 1 kg    |                                         |
| Bambu Lab | PLA Basic | Clear           | 1 kg    |                                         |
| Bambu Lab | PLA Basic | Red             | 1 kg    |                                         |
| Bambu Lab | PETG      | Red             | 1 kg    | Refill spool                            |
| Bambu Lab | PETG      | Blue            | 1 kg    | Refill spool                            |
| Bambu Lab | PETG      | Black           | 1 kg    | Refill spool                            |
| SUNLU     | PLA       | Black           | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | White           | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Grey            | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Red             | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Light Blue      | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Light Yellow    | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Green           | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Orange          | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Pink            | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Lavender Purple | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Brown           | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Olive Green     | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Oak             | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Skin            | 0.25 kg | Sampler pack                            |
| SUNLU     | PLA       | Transparent     | 0.25 kg | Sampler pack                            |
| TECBEARS  | PLA Matte | Black           | 10 kg   | High-speed rated (600 mm/s), bulk stock |

---

## Resin — Anycubic Photon Mono 2

Mono LCD resin printer. Used for detail parts — scout badges, finer geometry — where FDM resolution isn't enough. Paired with an Anycubic Wash & Cure 3 for post-processing.

|                 |                                        |
|-----------------|----------------------------------------|
| Build volume    | 143 × 89 × 165 mm                      |
| Screen          | 6.6" Mono LCD, 4096 × 2560, ~2000 hrs  |
| XY resolution   | 34 μm                                  |
| Z accuracy      | 10 μm (single linear rail)             |
| Print speed     | ≤ 50 mm/hr                             |
| Leveling        | 4-point manual                         |
| Light source    | Parallel matrix                        |
| Build platform  | Laser-engraved aluminium alloy         |
| Data input      | USB Type-A 2.0                         |

**Wash & Cure 3**

|               |                         |
|---------------|-------------------------|
| Wash capacity | Fits Mono 2 build plate |
| UV wavelength | 405 nm                  |
| Cure time     | ~2–3 min                |

**Resin on hand**

| Resin        | Type     | Colour            | Qty     | Notes                    |
|--------------|----------|-------------------|---------|--------------------------|
| ABS-Like V2  | ABS-Like | Black             | ~3 kg   | Structural / strength    |
| ABS-Like 2.0 | ABS-Like | Beige             | 8 kg    |                          |
| ABS-Like 2.0 | ABS-Like | Translucent Green | 1 kg    |                          |
| ABS-Like 2.0 | ABS-Like | Clear             | 1 kg    | For lens work eventually |
| Standard V2  | Standard | Black             | ~0.5 kg | Display / detail         |
| Standard     | Standard | Light Beige       | 8 kg    |                          |
| Standard     | Standard | Translucent Green | 1 kg    |                          |
| Standard     | Standard | Clear             | 1 kg    | For lens work eventually |
| Craftsman    | Detail   | Grey              | ~1 kg   | Sharp detail, brittle    |

*Detailed resin mixing notes and maintenance log kept separately.*

---

## Slicer / Workflow

*Notes to follow — slicer setup, print profiles, export workflow.*

---

**Rack and homelab prints**: [3D Printed Rack Parts](/homelab/rack-3d-prints/)
