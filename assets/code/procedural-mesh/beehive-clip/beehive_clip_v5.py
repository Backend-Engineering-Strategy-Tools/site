# Beehive Frame Spacer Clip v5
# Top-mount C-clip: straddles the frame top bar from above.
#
# v5 vs v3:
#   BAR_GRIP  14 → 17 mm  arms 3 mm longer
#   3 ramp teeth per arm (v3 style: long angled entry, horizontal catch)
#     BARB_Y1 =  8.5 mm  upper tooth
#     BARB_Y2 = 12.0 mm  middle tooth (same position as v3)
#     BARB_Y3 = 15.5 mm  lower tooth (~0.5 mm clearance to arm tip)
#   Between teeth: explicit arm-face vertex gives a short flat segment before each tooth ramp.
#
# Axes:
#   X  – bar width direction
#   Y  – vertical (+Y above bar top, −Y arm hang depth)
#   Z  – bar length (extrusion axis, 0 → CLIP_LEN)
#
# Print orientation: on its side — face-up arm carries text (last to print = clearest surface).
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, mathutils
from mathutils import Vector

# ── CONFIG ───────────────────────────────────────────────────────────────────

BAR_W      = 24.0
BAR_GRIP   = 17.5   # ← v5: 14 + 3.5 mm  (extra 0.5 mm gives ramp clearance at arm tip)
BAR_SPACER =  6.0
WALL       =  6.0
WALL_TOP   =  3.0
CLIP_LEN   =  8.0

# Ramp teeth (v3 style: diagonal ramp entry, horizontal catch)
BARB_BITE  =  1.5
BARB_W     =  3.0
# Three teeth per arm; middle at 12.0 mm = same as v3
BARB_Y1    =  8.5   # upper tooth  (upper edge 7.0 mm from bar top)
BARB_Y2    = 12.0   # middle tooth (same as v3)
BARB_Y3    = 15.5   # lower tooth  (lower edge 17.0 mm, 0.5 mm clear of arm tip)

INSCRIPTION_ARMS         = True
INS_LEFT                 = "B.E.S.T"   # left arm cross-section on Z=CLIP_LEN end face
INS_RIGHT                = "V5"         # right arm cross-section
INS_LEFT_SIZE            = 3.5          # mm cap height  (7 chars w/ dots ≈ 11 mm → fits 12 mm arm)
INS_RIGHT_SIZE           = 6.0          # mm cap height  (2 chars ≈ 8 mm → fits 12 mm arm)
INS_DEPTH                = 1.0          # mm cut depth  (matches rack_support_brace)

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
    Three ramp teeth per arm — identical V3 tooth shape (diagonal entry ramp, horizontal
    catch), repeated at BARB_Y1 / BARB_Y2 / BARB_Y3.  Flat vertex list like V3.

    Right arm inner face (tip → bridge):
        (hw,      -BAR_GRIP)       arm tip
        (hw-BITE, -(by3+bw2))      tooth 3 foot  ← 0.5 mm diagonal ramp from tip
        (hw-BITE, -by3)            tooth 3 inner face
        (hw,      -(by3-bw2))      tooth 3 top   → 0.5 mm diagonal ramp to tooth 2
        (hw-BITE, -(by2+bw2))      tooth 2 foot
        ... repeated for tooth 2, tooth 1 ...
        (hw,      0)               inner top-right

    Left arm: mirror traversed top-to-bottom.

    All inter-tooth segments are diagonal (X and Y both change) — no horizontal flat
    arm-face inserts between teeth, matching the V3 ramp character exactly.
    """
    mm  = 0.001
    hw  = BAR_W / 2
    ow  = WALL + BAR_SPACER
    bw2 = BARB_W / 2
    by1 = BARB_Y1
    by2 = BARB_Y2
    by3 = BARB_Y3

    def v(x, y):
        return Vector((x * mm, y * mm, 0.0))

    profile = [
        v(-(hw + ow),        +WALL_TOP),
        v(+(hw + ow),        +WALL_TOP),
        v(+(hw + ow),        -BAR_GRIP),
        # right arm inner — 3 ramp teeth (tip → bridge)
        v(+(hw),             -BAR_GRIP),           # arm tip inner
        v(+(hw - BARB_BITE), -(by3 + bw2)),        # tooth 3 foot  ← ramp from tip
        v(+(hw - BARB_BITE), -by3),                # tooth 3 inner face
        v(+(hw),             -(by3 - bw2)),        # tooth 3 top   → ramp to tooth 2
        v(+(hw - BARB_BITE), -(by2 + bw2)),        # tooth 2 foot  ← ramp
        v(+(hw - BARB_BITE), -by2),                # tooth 2 inner face
        v(+(hw),             -(by2 - bw2)),        # tooth 2 top   → ramp to tooth 1
        v(+(hw - BARB_BITE), -(by1 + bw2)),        # tooth 1 foot  ← ramp
        v(+(hw - BARB_BITE), -by1),                # tooth 1 inner face
        v(+(hw),             -(by1 - bw2)),        # tooth 1 top
        # bridge underside
        v(+(hw),             0),
        v(-(hw),             0),
        # left arm inner — 3 ramp teeth (bridge → tip), mirrored
        v(-(hw),             -(by1 - bw2)),        # tooth 1 top
        v(-(hw - BARB_BITE), -by1),                # tooth 1 inner face
        v(-(hw - BARB_BITE), -(by1 + bw2)),        # tooth 1 foot  → ramp to tooth 2 top
        v(-(hw),             -(by2 - bw2)),        # tooth 2 top   ← ramp
        v(-(hw - BARB_BITE), -by2),                # tooth 2 inner face
        v(-(hw - BARB_BITE), -(by2 + bw2)),        # tooth 2 foot  → ramp to tooth 3 top
        v(-(hw),             -(by3 - bw2)),        # tooth 3 top   ← ramp
        v(-(hw - BARB_BITE), -by3),                # tooth 3 inner face
        v(-(hw - BARB_BITE), -(by3 + bw2)),        # tooth 3 foot  → ramp to arm tip
        v(-(hw),             -BAR_GRIP),           # arm tip inner
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

print("Building beehive frame spacer clip v5 (3 ramp teeth, longer arms)…")
clip = build_clip()

if INSCRIPTION_ARMS:
    add_z_face_inscriptions(clip)

if EXPORT_STL:
    export_stl(clip, "beehive_clip_v5")

print("Done.")
print(f"  arm depth     (Y): {BAR_GRIP:.1f} mm  (v5: +3.5 mm vs v3)")
print(f"  top bridge    (Y): {WALL_TOP:.1f} mm  (solid)")
print(f"  teeth (Y from bar top): {BARB_Y1:.1f} / {BARB_Y2:.1f} / {BARB_Y3:.1f} mm")
print(f"  tooth: bite={BARB_BITE:.1f} mm  height={BARB_W:.1f} mm  (ramp style)")

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
