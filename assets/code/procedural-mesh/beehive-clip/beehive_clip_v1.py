# Beehive Frame Spacer Clip v1
# C-shaped (horseshoe) clip that snaps onto the side edge of a hive frame top bar.
# Barbed inner arms grip the bar face to prevent the clip from sliding off.
# The solid spacer face protrudes 6 mm proud of the bar edge — when two adjacent
# frames each carry a clip their spacer faces push against each other, holding
# exactly BAR_SPACER mm of bee-space between the frame bars.
#
# Axes used in this script:
#   X  – depth direction  (negative = outward / spacer face,  positive = into bar)
#   Y  – bar thickness    (±ht = bar top/bottom surface,  0 = centreline)
#   Z  – bar length       (0 … CLIP_LEN, the extrusion axis)
#
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, mathutils
from mathutils import Vector

# ── CONFIG ───────────────────────────────────────────────────────────────────

# Frame bar being clipped onto
BAR_T      = 20.0   # mm  bar thickness top-to-bottom  (inner channel Y span)
BAR_GRIP   = 10.0   # mm  how far the arms reach onto the bar (inner channel X depth)

# Clip body
BAR_SPACER =  6.0   # mm  protrusion proud of bar edge → the gap this clip creates
WALL       =  2.5   # mm  arm wall thickness (Y)
CLIP_LEN   = 15.0   # mm  clip length along bar (Z)

# Barb geometry — triangular tooth on inner face of each arm
BARB_BITE  =  1.5   # mm  how far the barb bites inward (toward bar centreline)
BARB_W     =  3.0   # mm  barb tooth width (X)
BARB_X     =  5.0   # mm  barb X position measured from bar edge (inside channel)
             #      must satisfy: BARB_W/2 < BARB_X < BAR_GRIP − BARB_W/2

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
    Constructs the 2-D horseshoe profile in the XY plane then extrudes it along Z.

    Profile cross-section layout:

          spacer face (X = -BAR_SPACER)
          │
          │  ┌─────────────────────────────────── arm tip outer (X = BAR_GRIP)
          ▼  │
     ┌────┴──┘   outer top face
     │           wall (Y = ht + WALL)
     │  ┌──────── inner top face with barb ─────── open end
     │  │         bar channel (Y = ht)
     │  │  ◄—barb—►
     │  │
     │  └──────── inner bottom face with barb ───── open end
     │           wall (Y = -(ht + WALL))
     └────┬──┐   outer bottom face
          │  └─────────────────────────────────── arm tip outer
          │
          spacer face (solid from X = -BAR_SPACER to X = 0)
    """
    mm   = 0.001       # mm → metres (Blender internal unit)
    ht   = BAR_T  / 2
    bx   = BARB_X
    bw2  = BARB_W / 2

    def v(x, y):
        return Vector((x * mm, y * mm, 0.0))

    # Profile polygon — traced clockwise viewed from +Z.
    # Region X = -BAR_SPACER … 0 is fully solid (the spacer bump).
    # Region X = 0 … BAR_GRIP is the open channel where the bar sits.
    profile = [
        # outer top-left  (spacer face, top corner)
        v(-BAR_SPACER,         ht + WALL),
        # outer top-right (arm tip outer)
        v( BAR_GRIP,           ht + WALL),
        # inner top, arm tip  (channel open end)
        v( BAR_GRIP,           ht),
        # inner top arm — trace right→left with barb tooth
        v( bx + bw2,           ht),
        v( bx,                 ht - BARB_BITE),   # barb tip ↓ (bites into bar top)
        v( bx - bw2,           ht),
        # inner top, back-wall junction (X = 0, bar edge)
        v( 0,                  ht),
        # inner back wall, top→bottom (solid spacer region, straight drop)
        v( 0,                 -ht),
        # inner bottom arm — trace left→right with barb tooth
        v( bx - bw2,          -ht),
        v( bx,                -ht + BARB_BITE),   # barb tip ↑ (bites into bar bottom)
        v( bx + bw2,          -ht),
        # inner bottom, arm tip  (channel open end)
        v( BAR_GRIP,          -ht),
        # outer bottom-right (arm tip outer)
        v( BAR_GRIP,          -(ht + WALL)),
        # outer bottom-left  (spacer face, bottom corner)
        v(-BAR_SPACER,        -(ht + WALL)),
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
    export_stl(clip, "beehive_clip_v1")

print("Done.")
print(f"  bar thickness  (Y channel)  : {BAR_T:.1f} mm")
print(f"  arm grip depth (X into bar) : {BAR_GRIP:.1f} mm")
print(f"  spacer bump    (X outward)  : {BAR_SPACER:.1f} mm  ← bee-space gap")
print(f"  wall thickness              : {WALL:.1f} mm")
print(f"  clip length    (Z)          : {CLIP_LEN:.1f} mm")
print(f"  barb bite                   : {BARB_BITE:.1f} mm  at X={BARB_X:.1f} mm from bar edge")

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
