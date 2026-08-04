# Raised foot for OpenBuilds V-Slot extrusion -- TRACK_COUNT below switches
# between a single-track (2020) and dual-track (2040) version.
#
# The downloaded E3X_raised_foot.stl in this folder is a confirmed-fit
# reference for 2040 (two tracks side by side, keys 20mm apart) -- doesn't
# fit a plain single-track bar, only one of its two keys would ever engage.
# This script builds either variant from scratch:
# - KEY profile (neck width, peak width/height, tip taper) is measured off
#   that reference part, not assumed from generic T-slot dimensions -- an
#   earlier box+bevel approximation matched the neck/peak widths but held
#   the peak width flat over too much height, carrying more interference
#   material than the reference and printing too tight to seat. See
#   KEY_PROFILE below.
# - Everything (pedestal base/shoulder, the 45-degree chamfer between them,
#   and the key) is built by loft_rounded_rings() -- stacking rounded-rect
#   cross-sections and connecting them with side faces -- rather than by
#   boolean-unioning separate boxes or running a bevel modifier on cube
#   edges. The old edge-bevel approach silently produced corrupted/self-
#   intersecting geometry after a boolean union (passed manifold and
#   bounding-box checks, only caught by comparing renders); lofting a
#   profile directly sidesteps that whole class of bug.
# - Pedestal base is narrower than the shoulder (the shoulder matches the
#   real extrusion face width), so the base-to-shoulder step is an outward
#   overhang -- PEDESTAL_CHAMFER_HEIGHT tapers it at ~45 degrees so it
#   prints without support instead of as a sharp 90-degree ledge.
#
# Run headless:
#   blender --background --python foot.py

import bpy
import bmesh
import math
import mathutils
import os

# ----------------------------
# CONFIG
# ----------------------------
TRACK_COUNT = 1   # 1 = single 2020 track, 2 = dual 2040 (two tracks, side by side)
SLOT_PITCH  = 20.0   # mm -- center-to-center spacing between tracks when TRACK_COUNT == 2
                      # (standard 20-series module pitch -- 2040 is two 2020s side by side)

if TRACK_COUNT == 1:
    BASE_X     = 16.0   # mm -- bottom box footprint (floor contact), across the bar
    SHOULDER_X = 20.0   # mm -- top box footprint, matches a real 2020 face width (was
                         # 28mm, overhanging well past the actual 20mm bar)
else:
    BASE_X     = 36.0   # mm -- wide enough to span both tracks
    SHOULDER_X = 40.0   # mm -- matches a real 2040 face width, margin either side of the keys

BASE_Y      = 40.0   # mm -- bottom box footprint, along the bar
BASE_HEIGHT =  7.0   # mm
BASE_CORNER_RADIUS = 3.0   # mm -- rounded corners

SHOULDER_Y      = 44.0   # mm -- top box footprint (bigger than the base -- the flare
                          # the key sits on, echoing the original's wider crown), centered
SHOULDER_HEIGHT =  8.0   # mm
SHOULDER_CORNER_RADIUS = 4.0   # mm

# The base-to-shoulder step is an outward overhang (shoulder is wider), which
# printed as a sharp 90 degree ledge. PEDESTAL_CHAMFER_HEIGHT tapers that
# step at ~45 degrees instead, sized off the actual X/Y margins so it comes
# out at 45 automatically -- both variants happen to use the same 4mm
# base-to-shoulder margin on X and Y, so a single height works for both axes.
assert (SHOULDER_X - BASE_X) == (SHOULDER_Y - BASE_Y), \
    "45-degree pedestal chamfer assumes equal X/Y base-to-shoulder margins"
PEDESTAL_CHAMFER_HEIGHT = (SHOULDER_X - BASE_X) / 2   # mm

CORNER_SEGMENTS = 4   # points per rounded corner

# T-slot key -- OpenBuilds V-Slot profile. Built as a lofted stack of
# rounded-rect rings, not a stem+head box pair with a bevel modifier -- the
# box+bevel version held its max width flat across ~2.6mm of engagement
# height (the bevel only eats material near the top/bottom edges), which is
# measurably more interference material than the reference part ever
# carries and was too tight to seat.
#
# KEY_PROFILE is the actual measured curve off the bundled E3X reference STL
# (bisect_plane slice-scan at 60 heights, connected-component width per
# slice), height-normalized -- not a hand-picked approximation. It starts
# WIDE at the shoulder line (~9mm) and flares down to the ~5.8mm neck
# minimum over the first ~27% of the height (a ~45-degree root fillet,
# clearly visible comparing renders against the reference), then bulges to
# a ~9.6mm peak before tapering to a ~6.6mm tip. KEY_TOTAL_HEIGHT (5.8mm) is
# also measured off the reference, not the earlier 8.0mm guess -- that 2.2mm
# difference was making the whole part visibly taller than the reference.
KEY_TOTAL_HEIGHT = 5.8   # mm
KEY_LENGTH       = 24.0  # mm -- engagement length along the bar (slide-in from the end)
KEY_PROFILE = [
    (0.000, 8.96),   # root, at the pedestal/shoulder line -- flares down from here
    (0.067, 8.19),
    (0.133, 7.43),
    (0.200, 6.66),
    (0.267, 5.89),   # neck minimum -- slot mouth pass-through width
    (0.333, 6.12),
    (0.400, 6.98),
    (0.467, 7.84),
    (0.533, 8.70),
    (0.600, 9.55),
    (0.667, 9.66),   # peak -- captured width inside the channel
    (0.733, 8.91),
    (0.800, 8.15),
    (0.867, 7.38),
    (0.933, 6.61),
    (1.000, 6.00),   # tip
]
KEY_CORNER_RADIUS = 1.8   # mm -- corner rounding on the loft's rounded-rect rings

KEY_X_OFFSETS = (0.0,) if TRACK_COUNT == 1 else (-SLOT_PITCH / 2, SLOT_PITCH / 2)

SCREW_HOLE_DIAM = 5.5   # mm -- M5 clearance, through-bolt up into a T-nut in the channel

UNION_OVERLAP = 0.3   # mm -- every stacked/adjacent piece extends this far into its
                       # neighbor before the boolean union, so touching pieces actually
                       # overlap instead of being coplanar (coplanar/zero-gap unions are
                       # exactly the case the EXACT solver can silently fail to merge --
                       # it'll happily report a "successful" union that's still two
                       # disconnected solids, which is what happened here originally)

TRACK_LABEL = "single_track" if TRACK_COUNT == 1 else "dual_track"

EXPORT_DIR   = os.path.dirname(os.path.abspath(__file__))
EXPORT_STL   = True
EXPORT_RENDER = True
RENDER_RES = (1600, 900)

# ----------------------------
# UTILITIES
# ----------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)

def boolean(target, cutter, operation):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="bool", type='BOOLEAN')
    mod.operation = operation
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="bool")
    bpy.data.objects.remove(cutter, do_unlink=True)

# ----------------------------
# GEOMETRY
# ----------------------------
def rounded_rect_profile(size_x, size_y, radius, segments):
    """Closed CCW loop of (x, y) points for a rounded rectangle centered on
    the origin -- a plain 4-point rectangle if radius <= 0."""
    if radius <= 0:
        return [(-size_x / 2, -size_y / 2), (size_x / 2, -size_y / 2),
                (size_x / 2, size_y / 2), (-size_x / 2, size_y / 2)]

    hx, hy = size_x / 2 - radius, size_y / 2 - radius
    corners = [(hx, hy, 0), (-hx, hy, 90), (-hx, -hy, 180), (hx, -hy, 270)]
    points = []
    for cx, cy, start_deg in corners:
        for i in range(segments + 1):
            a = math.radians(start_deg + 90 * i / segments)
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return points

def loft_rounded_rings(name, rings, segments=CORNER_SEGMENTS, x_center=0.0):
    """Solid built by stacking rounded-rect cross-sections and connecting
    consecutive rings with quad side faces, capped top and bottom. rings is
    a list of (z, size_x, size_y, radius) ordered bottom to top -- widening,
    narrowing, or holding steady between any two rings all fall out of this
    the same way, so it covers a straight extrusion (make_rounded_box's old
    job), a 45-degree taper (the pedestal chamfer), and an arbitrary profile
    curve (the key) with one function instead of three."""
    bm = bmesh.new()
    vert_rings = []
    for z, size_x, size_y, radius in rings:
        profile = rounded_rect_profile(size_x, size_y, radius, segments)
        vert_rings.append([bm.verts.new((x + x_center, y, z)) for x, y in profile])

    n = len(vert_rings[0])
    bottom_face = bm.faces.new(vert_rings[0])
    for ring_a, ring_b in zip(vert_rings, vert_rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ring_a[i], ring_a[j], ring_b[j], ring_b[i]))
    top_face = bm.faces.new(vert_rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# Pedestal top is the naive sum now -- the loft is one continuous mesh, no
# boolean union eating into the stack via UNION_OVERLAP. Computed once here
# so make_key() and the renderer can't drift out of sync with it.
PEDESTAL_TOP = BASE_HEIGHT + PEDESTAL_CHAMFER_HEIGHT + SHOULDER_HEIGHT
TOTAL_HEIGHT = PEDESTAL_TOP + KEY_TOTAL_HEIGHT

def make_pedestal():
    rings = [
        (0.0, BASE_X, BASE_Y, BASE_CORNER_RADIUS),
        (BASE_HEIGHT, BASE_X, BASE_Y, BASE_CORNER_RADIUS),
        (BASE_HEIGHT + PEDESTAL_CHAMFER_HEIGHT, SHOULDER_X, SHOULDER_Y, SHOULDER_CORNER_RADIUS),
        (PEDESTAL_TOP, SHOULDER_X, SHOULDER_Y, SHOULDER_CORNER_RADIUS),
    ]
    return loft_rounded_rings(f"foot_{TRACK_LABEL}", rings)

def make_key(x_offset=0.0):
    # First ring sits UNION_OVERLAP below the pedestal top, same width as the
    # neck (KEY_PROFILE's t=0), so it's embedded in the pedestal rather than
    # coplanar with it -- coplanar/zero-gap unions are exactly the case the
    # EXACT boolean solver can silently fail to merge (see header note).
    rings = [(PEDESTAL_TOP - UNION_OVERLAP, KEY_PROFILE[0][1], KEY_LENGTH, KEY_CORNER_RADIUS)]
    for t, width in KEY_PROFILE:
        radius = max(0.4, min(KEY_CORNER_RADIUS, width / 2 - 0.4))
        rings.append((PEDESTAL_TOP + t * KEY_TOTAL_HEIGHT, width, KEY_LENGTH, radius))
    return loft_rounded_rings("key", rings, x_center=x_offset)

def make_screw_hole_cutter():
    depth = TOTAL_HEIGHT + 2   # through the whole part, +margins top/bottom
    z = TOTAL_HEIGHT / 2 - 1
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=SCREW_HOLE_DIAM / 2,
        depth=depth,
        location=(0, 0, z),
    )
    return bpy.context.active_object

# ----------------------------
# RENDER (same convention as the other procedural-mesh scripts)
# ----------------------------
def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(200, -200, 400))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.angle = math.radians(5)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

def setup_material(obj):
    mat = bpy.data.materials.new("render_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.65, 0.65, 0.70, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def point_camera(cam_obj, target_pos, up=mathutils.Vector((0, 1, 0))):
    """Explicit look-at matrix, not a to_track_quat()/TRACK_TO shortcut --
    those go degenerate (arbitrary roll) exactly when the view direction is
    parallel to the up-axis hint, which the front/back views here hit
    dead-on (both straight along Y). Building the matrix by hand sidesteps
    that; RENDER_ANGLES below still nudges those directions off-axis
    slightly as a second safety margin."""
    direction = (target_pos - cam_obj.location).normalized()
    right = direction.cross(up).normalized()
    true_up = right.cross(direction).normalized()
    rot = mathutils.Matrix((right, true_up, -direction)).transposed().to_4x4()
    cam_obj.matrix_world = mathutils.Matrix.Translation(cam_obj.location) @ rot

RENDER_ANGLES = {   # same convention as scarf_slide.py / inspect_foot.py
    "front": (0.0, -1.0, 0.15),
    "side": (1.0, -0.1, 0.15),
    "top": (0.001, -0.3, 1.0),
    "bottom": (0.001, -0.3, -1.0),
    "iso": (0.6, -1.0, 0.6),
}

def render_views(obj, render_dir):
    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = RENDER_RES[0]
    scene.render.resolution_y = RENDER_RES[1]
    scene.render.image_settings.file_format = 'PNG'

    setup_lighting()
    setup_material(obj)

    center = mathutils.Vector((0.0, 0.0, TOTAL_HEIGHT / 2))
    D = max(BASE_X, BASE_Y, SHOULDER_X, SHOULDER_Y, TOTAL_HEIGHT) * 4.0

    bpy.ops.object.camera_add(location=(0, 0, 0))
    cam = bpy.context.active_object
    scene.camera = cam

    os.makedirs(render_dir, exist_ok=True)
    for label, direction in RENDER_ANGLES.items():
        dir_vec = mathutils.Vector(direction).normalized()
        cam.location = center + dir_vec * D
        # Keep world Z vertical in-frame (the usual CAD-drawing convention)
        # except for top/bottom, where the view direction IS Z -- there,
        # world Y has to serve as the up-hint instead.
        up = mathutils.Vector((0, 1, 0)) if abs(dir_vec.z) > 0.9 else mathutils.Vector((0, 0, 1))
        point_camera(cam, center, up=up)
        out = os.path.join(render_dir, f"{label}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"  rendered -> {out}")

# ----------------------------
# EXPORT
# ----------------------------
def export_stl(obj, path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"  exported -> {path}")

# ----------------------------
# MAIN
# ----------------------------
def main():
    clear_scene()

    pedestal = make_pedestal()

    for x_offset in KEY_X_OFFSETS:
        key = make_key(x_offset)
        boolean(pedestal, key, 'UNION')

    hole = make_screw_hole_cutter()
    boolean(pedestal, hole, 'DIFFERENCE')

    if EXPORT_STL:
        export_stl(pedestal, os.path.join(EXPORT_DIR, f"foot_{TRACK_LABEL}.stl"))

    if EXPORT_RENDER:
        render_views(pedestal, os.path.join(EXPORT_DIR, f"renders_{TRACK_LABEL}"))

    print("Done.")

if __name__ == "__main__":
    main()
