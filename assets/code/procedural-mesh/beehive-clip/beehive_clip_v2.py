# Beehive Frame Spacer Clip v2
# Top-mount C-clip: straddles the frame top bar from above.
# Two arms hang down and grip the bar's left and right faces.
# The right arm's outer face protrudes BAR_SPACER (6 mm) beyond the bar — the bee-space bump.
# Barbs on inner arm faces prevent the clip from working loose.
#
# Axes:
#   X  – bar width direction  (arms grip left/right bar faces; spacer protrudes on +X side)
#   Y  – vertical             (+Y = above bar top surface,  −Y = arm hang depth)
#   Z  – bar length           (extrusion axis, 0 → CLIP_LEN)
#
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, mathutils
from mathutils import Vector

# ── CONFIG ───────────────────────────────────────────────────────────────────

# Frame bar being clipped onto
BAR_W      = 24.0   # mm  bar width left–right  (inner channel X span) — actual wood: 24 mm
BAR_GRIP   =  8.0   # mm  arm hang depth below bar top surface (inner channel Y depth)

# Clip body
BAR_SPACER =  6.0   # mm  spacer protrusion on right arm outer face (bee-space bump)
WALL       =  6.0   # mm  arm wall thickness (X, both sides)
WALL_TOP   =  2.0   # mm  top bridge thickness (Y, above bar top surface) — the slim middle
CLIP_LEN   =  8.0   # mm  clip length along bar (Z)

# Barb — symmetric triangle tooth on inner face of each arm
BARB_BITE  =  1.5   # mm  inward bite (X toward bar centre)
BARB_W     =  3.0   # mm  tooth height (Y)
BARB_Y     =  6.0   # mm  barb centre depth from bar top  (near arm tip, not at it)
             #      must satisfy: BARB_W/2 < BARB_Y  and  BARB_Y + BARB_W/2 < BAR_GRIP

EXPORT_STL = False
EXPORT_DIR = "//stl_output"   # relative to .blend, or use an absolute path

# ── UTILITIES ────────────────────────────────────────────────────────────────

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)

def export_stl(obj, fname):
    import os
    path = os.path.join(bpy.path.abspath(EXPORT_DIR), fname + ".stl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"  → {path}")

# ── BUILD ────────────────────────────────────────────────────────────────────

def build_clip():
    """
    Cross-section in the XY plane (Z = extrusion axis):

      Y+  (up)
      ↑
      │  (−hw−WALL−SPACER, +WALL_TOP)       (+hw+WALL+BAR_SPACER, +WALL_TOP)
      │       ┌────────────────────────────────────────────┐
      │       │       top bridge  (WALL_TOP = 2 mm)        │
      │       ├──────────────────────────────────┬─────────┤  ← Y = 0  (bar top surface)
      │       │                                  │         │
      │  left │    inner channel                 │  right  │
      │  arm  │    (bar slides in from below)    │  arm    │
      │       │    BAR_W wide × BAR_GRIP deep    │         │
      │       │                                  │         │
      │       │  ◄ ramp barb: angled entry face, │         │
      │       │    horizontal catch (hard off) ► │         │
      │       ╧                                  ╧         │
      │  (−hw−WALL−SPACER, −BAR_GRIP)   (+hw+WALL+BAR_SPACER, −BAR_GRIP)
      └───────────────────────────────────────────────────→ X

    Both arms identical width (WALL + BAR_SPACER each side).
    Ramp barb: long angled face (easy slide in from below), horizontal catch face (hard pull-off).
    Ramp runs from arm tip (Y = -BAR_GRIP) up to catch (Y = -BARB_Y).
    """
    mm  = 0.001
    hw  = BAR_W / 2
    by  = BARB_Y
    bw2 = BARB_W / 2
    ow  = WALL + BAR_SPACER   # outer arm width (same both sides)

    def v(x, y):
        return Vector((x * mm, y * mm, 0.0))

    profile = [
        # ─ outer top-left ─────────────────────────────────────────────────
        v(-(hw + ow),            +WALL_TOP),
        # ─ outer top-right ────────────────────────────────────────────────
        v(+(hw + ow),            +WALL_TOP),
        # ─ outer bottom-right (arm tip outer) ─────────────────────────────
        v(+(hw + ow),            -BAR_GRIP),
        # ─ inner bottom-right (arm tip inner) ─────────────────────────────
        v(+(hw),                 -BAR_GRIP),
        # ─ right inner face — upward, symmetric triangle barb near tip ────
        v(+(hw),                 -(by + bw2)),   # below barb (0.5 mm above arm tip)
        v(+(hw - BARB_BITE),     -by),           # barb tip ←
        v(+(hw),                 -(by - bw2)),   # above barb
        # ─ inner top-right ────────────────────────────────────────────────
        v(+(hw),                 0),
        # ─ inner top-left ─────────────────────────────────────────────────
        v(-(hw),                 0),
        # ─ left inner face — downward, symmetric triangle barb near tip ───
        v(-(hw),                 -(by - bw2)),   # above barb
        v(-(hw - BARB_BITE),     -by),           # barb tip →
        v(-(hw),                 -(by + bw2)),   # below barb (0.5 mm above arm tip)
        # ─ inner bottom-left (arm tip inner) ──────────────────────────────
        v(-(hw),                 -BAR_GRIP),
        # ─ outer bottom-left (arm tip outer) ──────────────────────────────
        v(-(hw + ow),            -BAR_GRIP),
        # polygon closes back to outer top-left
    ]

    me = bpy.data.meshes.new("BeehiveClip")
    ob = bpy.data.objects.new("BeehiveClip", me)
    bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob

    bm = bmesh.new()
    verts = [bm.verts.new(p) for p in profile]
    face  = bm.faces.new(verts)

    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    top_verts = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top_verts, vec=Vector((0.0, 0.0, CLIP_LEN * mm)))

    bm.to_mesh(me)
    bm.free()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    return ob

# ── MAIN ─────────────────────────────────────────────────────────────────────

clear_scene()

print("Building beehive frame spacer clip…")
clip = build_clip()

if EXPORT_STL:
    print("Exporting…")
    export_stl(clip, "beehive_clip_v2")

print("Done.")
print(f"  bar channel width  (X): {BAR_W:.1f} mm")
print(f"  arm hang depth     (Y): {BAR_GRIP:.1f} mm")
print(f"  spacer bump        (X): {BAR_SPACER:.1f} mm  ← bee-space gap")
print(f"  arm wall thickness (X): {WALL:.1f} mm")
print(f"  top bridge         (Y): {WALL_TOP:.1f} mm")
print(f"  clip length        (Z): {CLIP_LEN:.1f} mm")
print(f"  barb bite (X): {BARB_BITE:.1f} mm  centre Y={BARB_Y:.1f} mm  height={BARB_W:.1f} mm")

# ── Zoom viewport to clip in isometric ortho view ────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
clip.select_set(True)
bpy.context.view_layer.objects.active = clip

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(area=area, region=region):
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'ORTHO'
            r3d.view_rotation = (
                mathutils.Euler(
                    (math.radians(54.7356), 0.0, math.radians(45.0)), 'XYZ'
                ).to_quaternion()
            )
            bpy.ops.view3d.view_selected()
        break
