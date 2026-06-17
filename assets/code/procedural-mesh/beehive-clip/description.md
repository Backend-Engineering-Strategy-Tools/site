# Beehive Frame Spacer Clip

A 3D-printable snap-on clip that maintains correct bee space between frames inside a hive body.

## Function

The clip straddles the frame top bar from above. Two arms hang down and grip the left and right faces of the bar. The right arm's outer face protrudes exactly 6 mm proud of the bar — the bee-space bump. When two adjacent frames each carry a clip the bumps push against each other and hold exactly 6 mm of bee space between the bars.

## Shape

Upside-down U / C-shape open at the bottom. Bar slides in from below.

```
      ┌──────────────────────┐   ← top bridge  (WALL_TOP = 2 mm)
      │                      │
 arm  │    inner channel     │  arm + 6 mm spacer bump
 (6mm)│    BAR_W × BAR_GRIP  │  (6 mm wall + 6 mm protrusion)
      │                      │
      └──  ▲ barbs ▲  ───────┘
           open end — bar slides in from below
```

- **Top bridge** — slim 2 mm piece bridging over the bar top
- **Both arms** — identical width (WALL + BAR_SPACER = 12 mm each side), symmetric
- **Barbs** — symmetric triangle tooth on each inner arm face; positioned near (but not at) the arm tip

## Parameters by version

| Parameter   | v2     | v3     | v4     | v5            |
|-------------|--------|--------|--------|---------------|
| BAR_W       | 24 mm  | 24 mm  | 24 mm  | 24 mm         |
| BAR_GRIP    | 8 mm   | 14 mm  | 14 mm  | 17.5 mm       |
| WALL_TOP    | 2 mm   | 3 mm   | 3 mm   | 3 mm          |
| CLIP_LEN    | 8 mm   | 8 mm   | 8 mm   | 8 mm          |
| Teeth       | 1×ramp | 1×ramp | 1×flat | 3×ramp        |
| BARB_Y      | 6 mm   | 12 mm  | 12 mm  | 8.5/12.0/15.5 |
| BARB_BITE   | 1.5 mm | 1.5 mm | 1.5 mm | 1.5 mm        |
| Inscription | —      | arms   | arms   | arms          |

**v3**: stiffer arch (WALL_TOP 2→3), longer arms (8→14), barb slides down. Arm inscriptions "B.E.S.T" / "V3". Print on side — face-up arm is last to print, shows text most clearly.

**v4**: flat/rectangular teeth instead of ramp. No angled entry face = harder to push on AND pull off. Maximum grip.

**v5**: arms 3.5 mm longer (14→17.5), 3 ramp teeth per arm at 8.5 / 12.0 / 15.5 mm from bar top. Middle tooth same position as v3. All inter-tooth segments are diagonal (same V3 ramp shape). Extra 0.5 mm arm length gives ramp clearance between arm tip and lowest tooth foot.

## Open questions

- Measure actual bar width — BAR_W must match
- Chamfer arm tips for easier initial snap-on?
- Spacer on both sides symmetrically (3 mm each) or one side only (6 mm)?
