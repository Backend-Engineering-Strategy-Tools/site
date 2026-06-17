# Beehive Frame Spacer Clip v3
# Top-mount C-clip: straddles the frame top bar from above.
# Two arms hang down and grip the bar's left and right faces.
# The right arm's outer face protrudes BAR_SPACER (6 mm) beyond the bar — the bee-space bump.
# Barbs on inner arm faces prevent the clip from working loose.
#
# v3 changes vs v2:
#   WALL_TOP  2 → 3 mm   stiffer top bridge (arch) — kept solid, no inscription
#   BAR_GRIP  8 → 14 mm  longer arms
#   BARB_Y    6 → 12 mm  barb slides down with arm tip (~0.5 mm clearance to tip)
#   Arm inscriptions: "B.E.S.T" on left arm outer face, "V3" on right arm outer face
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
BAR_GRIP   = 14.0   # mm  arm hang depth below bar top surface  ← v3: was 8

# Clip body
BAR_SPACER =  6.0   # mm  spacer protrusion on right arm outer face (bee-space bump)
WALL       =  6.0   # mm  arm wall thickness (X, both sides)
WALL_TOP   =  3.0   # mm  top bridge thickness (Y)  ← v3: stiffer arch — kept solid
CLIP_LEN   =  8.0   # mm  clip length along bar (Z)

# Barb — ramp tooth: long angled entry face (easy slide in), horizontal catch (hard pull-off)
BARB_BITE  =  1.5   # mm  inward bite (X toward bar centre)
BARB_W     =  3.0   # mm  tooth height (Y)
BARB_Y     = 12.0   # mm  barb centre depth from bar top  ← v3: was 6, slides down with arm
             #      check: 1.5 < 12 ✓   12 + 1.5 = 13.5 < 14 ✓  (0.5 mm clear of tip)

# Inscriptions — debossed into the Z=CLIP_LEN end face (same pattern as rack_support_brace.py)
# Print the clip standing on its Z=0 end face; Z=CLIP_LEN is last to print = cleanest surface.
# Each arm cross-section at that face: 12 mm wide (X) × 17 mm tall (Y) — more room than arm outer.
# "B.E.S.T" 7 chars × ~1.5 mm each ≈ 10.5 mm at 2.5 mm size — fits in 12 mm arm width.
INSCRIPTION_ARMS         = True
INS_LEFT                 = "B.E.S.T"   # left arm cross-section (centred on left arm X span)
INS_RIGHT                = "V3"         # right arm cross-section
INS_LEFT_SIZE            = 3.5          # mm cap height  (7 chars w/ dots ≈ 11 mm → fits 12 mm arm)
INS_RIGHT_SIZE           = 6.0          # mm cap height  (2 chars ≈ 8 mm → fits 12 mm arm)
INS_DEPTH                = 1.0          # mm cut depth into end face  (matches rack_support_brace)

EXPORT_STL = False
EXPORT_DIR = "//stl_output"

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
      │       │       top bridge  (WALL_TOP = 3 mm)        │  ← solid for stiffness
      │       ├──────────────────────────────────┬─────────┤  ← Y = 0  (bar top surface)
      │  B.   │                                  │         │ V
      │  E.   │    inner channel                 │  right  │ 3
      │  S.   │    (bar slides in from below)    │  arm    │  ← arm inscriptions
      │  T    │    BAR_W wide × BAR_GRIP deep    │         │
      │       │                                  │         │
      │       │  ◄ ramp barb                   ► │         │
      │       ╧                                  ╧         │
      └───────────────────────────────────────────────────→ X
    """
    mm  = 0.001
    hw  = BAR_W / 2
    by  = BARB_Y
    bw2 = BARB_W / 2
    ow  = WALL + BAR_SPACER

    def v(x, y):
        return Vector((x * mm, y * mm, 0.0))

    profile = [
        v(-(hw + ow),        +WALL_TOP),
        v(+(hw + ow),        +WALL_TOP),
        v(+(hw + ow),        -BAR_GRIP),
        v(+(hw),             -BAR_GRIP),
        v(+(hw - BARB_BITE), -(by + bw2)),
        v(+(hw - BARB_BITE), -by),
        v(+(hw),             -(by - bw2)),
        v(+(hw),             0),
        v(-(hw),             0),
        v(-(hw),             -(by - bw2)),
        v(-(hw - BARB_BITE), -by),
        v(-(hw - BARB_BITE), -(by + bw2)),
        v(-(hw),             -BAR_GRIP),
        v(-(hw + ow),        -BAR_GRIP),
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


# ── Z END-FACE INSCRIPTIONS ──────────────────────────────────────────────────

def add_z_face_inscriptions(clip):
    """
    Deboss text into the Z=CLIP_LEN end face — same pattern as rack_support_brace.py.
    No rotation: default text (XY plane, face normal +Z) points straight out of the end face.
    Print clip standing on Z=0 face; Z=CLIP_LEN is last to print = cleanest surface.
    Each arm cross-section: ow = 12 mm wide (X) × 17 mm tall (Y).
    """
    mm  = 0.001
    hw  = BAR_W / 2
    ow  = WALL + BAR_SPACER
    arm_y_mid = (WALL_TOP - BAR_GRIP) / 2 * mm
    z_inner   = (CLIP_LEN - INS_DEPTH) * mm

    def make_z_cutter(body, size, cx):
        bpy.ops.object.text_add(location=(cx * mm, arm_y_mid, z_inner))
        txt = bpy.context.object
        txt.data.body    = body
        txt.data.size    = size * mm
        txt.data.extrude = (INS_DEPTH + 0.5) * mm
        txt.data.align_x = 'CENTER'
        txt.data.align_y = 'CENTER'
        bpy.ops.object.convert(target='MESH')
        return bpy.context.object

    t_left  = make_z_cutter(INS_LEFT,  INS_LEFT_SIZE,  -(hw + ow / 2))
    t_right = make_z_cutter(INS_RIGHT, INS_RIGHT_SIZE, +(hw + ow / 2))

    bpy.ops.object.select_all(action='DESELECT')
    t_left.select_set(True)
    t_right.select_set(True)
    bpy.context.view_layer.objects.active = t_left
    bpy.ops.object.join()
    cutter = bpy.context.object
    cutter.name = "text_cutter"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = clip
    clip.select_set(True)

    mod = clip.modifiers.new("ZFaceInscription", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object    = cutter
    mod.solver    = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="ZFaceInscription")
    bpy.data.objects.remove(cutter, do_unlink=True)
    print(f"  engraved '{INS_LEFT}' / '{INS_RIGHT}' on Z end face ({INS_DEPTH} mm deep)")

# ── MAIN ─────────────────────────────────────────────────────────────────────

clear_scene()

print("Building beehive frame spacer clip v3…")
clip = build_clip()

if INSCRIPTION_ARMS:
    add_z_face_inscriptions(clip)

if EXPORT_STL:
    export_stl(clip, "beehive_clip_v3")

print("Done.")
print(f"  bar channel   (X): {BAR_W:.1f} mm")
print(f"  arm depth     (Y): {BAR_GRIP:.1f} mm")
print(f"  spacer bump   (X): {BAR_SPACER:.1f} mm")
print(f"  top bridge    (Y): {WALL_TOP:.1f} mm  (solid — stiffness)")
print(f"  clip length   (Z): {CLIP_LEN:.1f} mm")
print(f"  barb: bite={BARB_BITE:.1f} mm  centre Y={BARB_Y:.1f} mm  height={BARB_W:.1f} mm")
if INSCRIPTION_ARMS:
    print(f"  left arm:  '{INS_LEFT}'  {INS_LEFT_SIZE:.1f} mm cap height  (~{len(INS_LEFT)*1.3:.0f} mm along Z)")
    print(f"  right arm: '{INS_RIGHT}'  {INS_RIGHT_SIZE:.1f} mm cap height")

# ── Zoom viewport to isometric ortho ─────────────────────────────────────────
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
