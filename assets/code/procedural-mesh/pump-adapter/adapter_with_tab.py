"""
Pump-to-hose adapter (Blender bpy) - standalone, NOT terrain. V9.

Same part as pump_adapter_v8_sturdy_ear.py, ear geometry fixed again.

V8 built the ear as a full-size duplicate circle, offset sideways by a
FIXED distance the whole way up - which meant the ear's own bottom was
a flat disc (radius 0 to PLUG_OD_R at one Z), and after being shifted
sideways, most of that disc no longer had the main body sitting under
it: a real, wide flat overhang, the same mistake as V1/V4 just in a new
shape.

V9 fixes it by growing the OFFSET itself instead of holding it fixed:
the ear starts almost perfectly coincident with the main body (a tiny
0.5mm offset - not exactly 0, to avoid an exact-coincidence boolean
trap) and swings outward, offset growing linearly up to its full value,
at exactly SHOULDER_TAPER_ANGLE_DEG so the growth stays self-supporting.
Crucially the ear's RADIUS never shrinks - it stays exactly SOCKET_OD_R,
matching the socket wall itself, the entire way up. So unlike a
point-apex root, there's no narrow throat anywhere: even where the
ear's exposed crescent is thin (near the bottom, where the offset is
still small), that crescent is bonded along its full inner boundary to
the main body's own substantial wall, not funneled through a point.
Sturdy AND self-supporting, rather than having to pick one.

This only works because the growth happens entirely ABOVE the shoulder
taper (Z_SHOULDER_END onward), where the main body's own radius is
already constant (=SOCKET_OD_R) - growing the offset DURING the
shoulder's own taper would stack on top of a slope that's already near
the 45-degree limit and blow the budget (checked this by hand before
writing any code - see the arithmetic note in
feedback_functional_parts_pipeline for why).

Run: Blender -> Scripting workspace -> Open this file -> Alt+P
Or headless: blender --background --python pump_adapter_v9_no_overhang_ear.py
"""

import bpy
import bmesh
import math
import mathutils
import os

# ============================================================
# CONFIG (all mm)
# ============================================================

EXPORT_DIR = "/Users/mannil/Desktop/studio-m/TSONS/pump_adapter/output_v9"
EXPORT_STL = True

RENDER_IMAGES = True
RENDER_DIR = os.path.join(EXPORT_DIR, "renders")
RENDER_RESOLUTION = (1600, 900)
RENDER_ANGLES = {
    "front": (0.0, -1.0, 0.15),
    "side": (1.0, -0.1, 0.15),
    "top": (0.001, -0.3, 1.0),
    "iso": (0.6, -1.0, 0.6),
}

SPIN_STEPS = 128
EAR_SEGMENTS = 128  # matches SPIN_STEPS - a coarser facet density on the
                     # ear than the main body showed up as a visible
                     # "lip" seam under flat shading, even though the
                     # surfaces are geometrically continuous there

# --- Plug end (goes INTO the existing 18mm hole) ---
HOLE_ID = 18.0
PLUG_FIT_CLEARANCE = 0.4
PLUG_OD = HOLE_ID - PLUG_FIT_CLEARANCE   # 17.6mm land diameter
PLUG_INSERT_LEN = 7.0

# --- Shoulder taper - a smoothstep-eased curve (zero slope at both
# ends), not a straight line, so it blends tangentially into the flat
# plug land below and the vertical socket wall above with no kink at
# either junction. A smoothstep's steepest point (the middle) runs at
# 1.5x the straight-line-average rate, so SHOULDER_TAPER_LEN has to be
# longer than a straight taper would need for the same 45-degree limit -
# checked via SHOULDER_PEAK_ANGLE_DEG below rather than assumed. ---
SHOULDER_TAPER_LEN = 8.5
SHOULDER_CURVE_STEPS = 12   # sample points along the eased curve

# --- Socket end (slides OVER the pump's 23mm spigot) ---
PUMP_SPIGOT_OD = 23.0
SOCKET_FIT_CLEARANCE = 0.3
SOCKET_ID = PUMP_SPIGOT_OD + SOCKET_FIT_CLEARANCE   # 23.3mm
SOCKET_WALL_T = 2.5
SOCKET_DEPTH = 8.0
FLOOR_WEB_T = 2.0

# --- Through-bore (flow passage, end to end) ---
BORE_DIA = 10.0

# --- String ear (V9: growing offset, constant SOCKET_OD_R radius) ---
EAR_Z_MARGIN = 0.1          # ear starts this far above Z_SHOULDER_END -
                             # avoids sharing an exact Z with the main
                             # body's own taper-to-cylinder transition.
                             # Kept small - this gap plus EAR_OFFSET_START
                             # is what was reading as a visible "lip"
                             # where the ear meets the shoulder
EAR_OFFSET_START = 0.1      # tiny starting offset - not exactly 0, avoids
                             # an exact-coincidence boolean trap. Kept as
                             # small as practical for the same reason
EAR_OFFSET_MAX = 6.0        # final offset - how far the loop protrudes
EAR_GROWTH_ANGLE_DEG = 41.7 # ear's own growth rate - independent of the
                             # shoulder's own (now much shallower, since
                             # it was lengthened for the smoothstep) -
                             # this just needs to stay <=45 on its own,
                             # checked below
EAR_SHORTER_MIN = 2.0
EAR_SHORTER_MAX = 5.0
EAR_HOLE_DIA = 2.5
EAR_HOLE_Z_MARGIN = 1.5     # how far below the ear's own top the hole sits -
                             # needs to be high enough that the ear's local
                             # offset (hence its enclosing radius around the
                             # hole) is already large
EAR_HOLE_X_FRACTION = 0.5   # hole's X position, as a fraction of the way
                             # from the main OD out to the ear's local
                             # max extent at the hole's height - this is a
                             # VERTICAL hole (Z-axis): it works because the
                             # ear's circle comfortably encloses this (X, Y)
                             # point up near the top, then its own material
                             # recedes away from that same point well before
                             # reaching EAR_Z_START - so the hole opens into
                             # clear air on its own, lower down, without
                             # needing to be aimed at an "exit"
EAR_HOLE_OVERTRAVEL = 10.0   # how far past the ear's own Z-range the hole
                             # cutter extends - safe to be generous since
                             # neither the ear nor the main body has any
                             # material out at the hole's X position outside
                             # that range anyway
HOLLOW_CUTTER_CLEARANCE = 0.3
BOOL_CUTTER_MARGIN = 2.0

# --- Finishing ---
BEVEL_WIDTH = 0.3
BEVEL_SEGMENTS = 2

# ============================================================
# DERIVED
# ============================================================

PLUG_OD_R = PLUG_OD / 2
SOCKET_OD = SOCKET_ID + 2 * SOCKET_WALL_T
SOCKET_OD_R = SOCKET_OD / 2
SOCKET_ID_R = SOCKET_ID / 2
BORE_R = BORE_DIA / 2
SOCKET_LEN = SOCKET_DEPTH + FLOOR_WEB_T

# Average slope of the shoulder taper - reused (conservatively) as the
# ear's own growth rate below. The curve's STEEPEST point runs faster
# than this average (see SHOULDER_PEAK_ANGLE_DEG) - that's what's
# actually checked against the 45-degree print limit.
SHOULDER_TAPER_ANGLE_DEG = math.degrees(
    math.atan2(SOCKET_OD_R - PLUG_OD_R, SHOULDER_TAPER_LEN)
)
SHOULDER_PEAK_ANGLE_DEG = math.degrees(
    math.atan2(1.5 * (SOCKET_OD_R - PLUG_OD_R), SHOULDER_TAPER_LEN)
)

Z_TIP = 0.0
Z_SHOULDER_START = PLUG_INSERT_LEN
Z_SHOULDER_END = Z_SHOULDER_START + SHOULDER_TAPER_LEN
Z_SOCKET_FLOOR = Z_SHOULDER_END + FLOOR_WEB_T
Z_OPEN_END = Z_SHOULDER_END + SOCKET_LEN

EAR_Z_START = Z_SHOULDER_END + EAR_Z_MARGIN
EAR_GROWTH_H = (EAR_OFFSET_MAX - EAR_OFFSET_START) / math.tan(math.radians(EAR_GROWTH_ANGLE_DEG))
EAR_TOP_Z = EAR_Z_START + EAR_GROWTH_H
EAR_SHORTER_AMOUNT = Z_OPEN_END - EAR_TOP_Z


def _ear_offset_at(z):
    frac = (z - EAR_Z_START) / EAR_GROWTH_H
    return EAR_OFFSET_START + (EAR_OFFSET_MAX - EAR_OFFSET_START) * frac


# The hole is VERTICAL (Z-axis), centered at (EAR_HOLE_X, 0) - it works
# specifically because the ear's own circle (radius SOCKET_OD_R,
# constant) comfortably surrounds that (X, Y) point at Z=EAR_HOLE_Z, even
# though the ear's material recedes away from that same (X, Y) position
# well before it reaches EAR_Z_START - so the hole is fully enclosed up
# top and exits into open air lower down on its own, with nothing extra
# needed to make that happen. Confirmed by rendering straight down and
# straight up through the hole - solid ring both directions, not a
# lopsided notch.
EAR_HOLE_Z = EAR_TOP_Z - EAR_HOLE_Z_MARGIN
EAR_HOLE_LOCAL_OFFSET = _ear_offset_at(EAR_HOLE_Z)
EAR_HOLE_LOCAL_MAX_X = EAR_HOLE_LOCAL_OFFSET + SOCKET_OD_R
EAR_HOLE_X = SOCKET_OD_R + (EAR_HOLE_LOCAL_MAX_X - SOCKET_OD_R) * EAR_HOLE_X_FRACTION
EAR_HOLE_DIST_FROM_CENTER = EAR_HOLE_X - EAR_HOLE_LOCAL_OFFSET  # straight-line, since both sit at Y=0
EAR_HOLE_MARGIN = SOCKET_OD_R - EAR_HOLE_DIST_FROM_CENTER - EAR_HOLE_DIA / 2

assert BORE_R < PLUG_OD_R - 1.0, \
    "through-bore sits too close to the plug's outer wall - thin wall there"
assert BORE_R < SOCKET_ID_R, \
    "through-bore is bigger than the socket ID - shrink BORE_DIA"
assert SHOULDER_PEAK_ANGLE_DEG <= 45.0, \
    f"shoulder taper's steepest point (the curve's middle) is {SHOULDER_PEAK_ANGLE_DEG:.1f} deg off " \
    "vertical - lengthen SHOULDER_TAPER_LEN to keep it <=45"
assert EAR_GROWTH_ANGLE_DEG <= 45.0, \
    f"ear growth angle is {EAR_GROWTH_ANGLE_DEG:.1f} deg off vertical - lower it to keep it <=45"
assert EAR_SHORTER_MIN <= EAR_SHORTER_AMOUNT <= EAR_SHORTER_MAX, \
    f"ear top lands {EAR_SHORTER_AMOUNT:.1f}mm short of the socket's own top - needs to land between " \
    f"{EAR_SHORTER_MIN} and {EAR_SHORTER_MAX}mm short; tune EAR_OFFSET_MAX"
assert EAR_HOLE_X > SOCKET_OD_R, \
    "string hole isn't past the main body's own OD - it'd be buried, not in the protruding crescent"
assert EAR_HOLE_MARGIN >= 1.0, \
    f"string hole only has {EAR_HOLE_MARGIN:.2f}mm of surrounding material at that height - lower " \
    "EAR_HOLE_X_FRACTION, shrink EAR_HOLE_DIA, or grow EAR_OFFSET_MAX to widen the enclosed region"
EAR_HOLE_INNER_EDGE = EAR_HOLE_X - EAR_HOLE_DIA / 2
EAR_HOLE_MAIN_BODY_CLEARANCE = EAR_HOLE_INNER_EDGE - SOCKET_OD_R
assert EAR_HOLE_MAIN_BODY_CLEARANCE >= 0.5, \
    f"string hole's inner edge is only {EAR_HOLE_MAIN_BODY_CLEARANCE:.2f}mm past the main body's own OD - " \
    "the hole is cut into the ear BEFORE it's unioned onto the main body, so any part of the hole that " \
    "overlaps the main body's own solid gets filled back in by the union, biting the circle out of round. " \
    "Raise EAR_HOLE_X_FRACTION or shrink EAR_HOLE_DIA."


# ============================================================
# HELPERS (shared conventions - see brazier/brazier.py, columns/columns.py)
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)


def apply_boolean(target, cutter, operation):
    mod = target.modifiers.new("Bool", 'BOOLEAN')
    mod.object = cutter
    mod.operation = operation
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def apply_bevel(obj, width, segments=2):
    mod = obj.modifiers.new("Bevel", 'BEVEL')
    mod.width = width
    mod.segments = segments
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def compute_scene_bounds():
    xs, ys, zs = [], [], []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ mathutils.Vector(corner)
            xs.append(world_corner.x)
            ys.append(world_corner.y)
            zs.append(world_corner.z)
    if not xs:
        return mathutils.Vector((0.0, 0.0, 0.0)), 10.0
    center = mathutils.Vector((
        (min(xs) + max(xs)) / 2,
        (min(ys) + max(ys)) / 2,
        (min(zs) + max(zs)) / 2,
    ))
    size = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return center, size


def setup_camera_and_light(center):
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    target = bpy.data.objects.new("RenderTarget", None)
    target.location = center
    bpy.context.collection.objects.link(target)

    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    light_data = bpy.data.lights.new("RenderSun", type='SUN')
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("RenderSun", light_data)
    light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(35))
    bpy.context.collection.objects.link(light_obj)

    bpy.context.scene.camera = cam_obj
    return cam_obj


def render_angles(center, size):
    os.makedirs(RENDER_DIR, exist_ok=True)
    cam_obj = setup_camera_and_light(center)

    scene = bpy.context.scene
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = RENDER_RESOLUTION[0]
    scene.render.resolution_y = RENDER_RESOLUTION[1]

    distance = size * 4.0
    for name, direction in RENDER_ANGLES.items():
        cam_obj.location = center + mathutils.Vector(direction).normalized() * distance
        scene.render.filepath = os.path.join(RENDER_DIR, f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {scene.render.filepath}")


def export_stl(obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = os.path.join(EXPORT_DIR, filename)
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"Exported {path}")


def _smoothstep(t):
    return t * t * (3 - 2 * t)


def _curved_taper_points(r0, r1, z0, z1, steps):
    """Sample points along a smoothstep-eased curve from (r0, z0) to
    (r1, z1) - zero slope at both ends, so it blends tangentially into
    whatever meets it on either side instead of leaving a kink. Same
    technique as brazier.py's bowl-wall curve."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        te = _smoothstep(t)
        pts.append((r0 + (r1 - r0) * te, z0 + (z1 - z0) * t))
    return pts


def _spin_profile(profile, name, steps=SPIN_STEPS):
    """Revolve a closed (r, z) profile loop 360 degrees around the Z axis
    into a solid/shell mesh object."""
    bm = bmesh.new()
    verts = [bm.verts.new((r, 0.0, z)) for r, z in profile]
    edges = [bm.edges.new((verts[i], verts[i + 1])) for i in range(len(verts) - 1)]
    bmesh.ops.spin(
        bm, geom=verts + edges, axis=(0, 0, 1), cent=(0, 0, 0),
        steps=steps, angle=math.radians(360), use_merge=True,
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _build_cylinder(radius, length, center, name, axis='z', steps=32):
    """Cylinder along the given axis, centered at `center`."""
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=steps,
        radius1=radius, radius2=radius, depth=length,
    )
    if axis == 'y':
        bmesh.ops.rotate(
            bm, verts=bm.verts[:], cent=(0, 0, 0),
            matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'),
        )
    elif axis == 'x':
        bmesh.ops.rotate(
            bm, verts=bm.verts[:], cent=(0, 0, 0),
            matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'),
        )
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True)
    return obj


# ============================================================
# ADAPTER
# ============================================================

def build_body():
    shoulder = _curved_taper_points(
        PLUG_OD_R, SOCKET_OD_R, Z_SHOULDER_START, Z_SHOULDER_END, SHOULDER_CURVE_STEPS,
    )
    profile = (
        [(PLUG_OD_R, Z_TIP)]
        + shoulder
        + [
            (SOCKET_OD_R, Z_OPEN_END),
            (SOCKET_ID_R, Z_OPEN_END),
            (SOCKET_ID_R, Z_SOCKET_FLOOR),
            (BORE_R, Z_SOCKET_FLOOR),
            (BORE_R, Z_TIP),
        ]
    )
    profile.append(profile[0])
    return _spin_profile(profile, "pump_adapter_v9")


def build_ear_raw():
    """Loft between two rings, BOTH radius SOCKET_OD_R - the ear's
    radius never shrinks, only its center's offset from the main axis
    grows (EAR_OFFSET_START to EAR_OFFSET_MAX). Since the radius always
    matches the socket wall itself, there's no point/narrow-neck
    anywhere - the visible crescent starts almost invisibly thin (an
    exact match would be a boolean coincidence trap, hence the small
    EAR_OFFSET_START) and widens as the offset grows, but the material
    is bonded to the main body along its full inner boundary the whole
    way, not funneled through a point."""
    segs = EAR_SEGMENTS
    bm = bmesh.new()

    def ring(z, offset):
        return [
            bm.verts.new((
                offset + SOCKET_OD_R * math.cos(2 * math.pi * i / segs),
                SOCKET_OD_R * math.sin(2 * math.pi * i / segs),
                z,
            ))
            for i in range(segs)
        ]

    bottom = ring(EAR_Z_START, EAR_OFFSET_START)
    top = ring(EAR_TOP_Z, EAR_OFFSET_MAX)

    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new((bottom[i], top[i], top[j], bottom[j]))
    bm.faces.new(bottom)
    bm.faces.new(top)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("ear_raw")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("ear_raw", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_ear():
    """Cut the main body's own void shape back out of the ear (two plain
    cylinder cutters, bore-radius below the socket floor and socket-ID-
    radius above it, overlapping a bit at the handoff - see
    feedback_blender_boolean_fragility entry 10 for why a single
    stepped cutter isn't safe here), then cut the string hole - a
    VERTICAL cutter, deliberately run well past both ends of the ear.
    It doesn't need to be aimed carefully: above EAR_TOP_Z and below
    EAR_Z_START there's nothing there for it to over-cut (the ear only
    exists between those two heights, and the main body doesn't reach
    out this far in X either), so a generously long cutter just quietly
    removes nothing outside the ear's own material."""
    ear = build_ear_raw()

    r_bore = BORE_R + HOLLOW_CUTTER_CLEARANCE
    r_socket_id = SOCKET_ID_R + HOLLOW_CUTTER_CLEARANCE
    z0 = EAR_Z_START - 1.0
    z1 = EAR_TOP_Z + BOOL_CUTTER_MARGIN
    overlap = 1.0

    bore_len = (Z_SOCKET_FLOOR + overlap) - z0
    bore_center = (z0 + Z_SOCKET_FLOOR + overlap) / 2
    bore_cutter = _build_cylinder(r_bore, bore_len, (0.0, 0.0, bore_center), "ear_bore_void_cutter")
    apply_boolean(ear, bore_cutter, 'DIFFERENCE')

    socket_len = z1 - (Z_SOCKET_FLOOR - overlap)
    socket_center = (z1 + Z_SOCKET_FLOOR - overlap) / 2
    socket_cutter = _build_cylinder(r_socket_id, socket_len, (0.0, 0.0, socket_center), "ear_socket_void_cutter")
    apply_boolean(ear, socket_cutter, 'DIFFERENCE')

    hole_z0 = EAR_Z_START - EAR_HOLE_OVERTRAVEL
    hole_z1 = EAR_TOP_Z + EAR_HOLE_OVERTRAVEL
    hole_cutter = _build_cylinder(
        EAR_HOLE_DIA / 2, hole_z1 - hole_z0,
        (EAR_HOLE_X, 0.0, (hole_z0 + hole_z1) / 2), "ear_hole_cutter", axis='z',
    )
    apply_boolean(ear, hole_cutter, 'DIFFERENCE')

    return ear


def build_adapter():
    body = build_body()

    ear = build_ear()
    apply_boolean(body, ear, 'UNION')

    apply_bevel(body, BEVEL_WIDTH, BEVEL_SEGMENTS)
    return body


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    clear_scene()

    adapter = build_adapter()

    print(f"Plug end: OD {PLUG_OD}mm into {HOLE_ID}mm hole, land length {PLUG_INSERT_LEN}mm")
    print(f"Shoulder taper: {SHOULDER_TAPER_LEN}mm long, smoothstep-eased, peak "
          f"{SHOULDER_PEAK_ANGLE_DEG:.1f} deg off vertical (avg {SHOULDER_TAPER_ANGLE_DEG:.1f})")
    print(f"Socket end: ID {SOCKET_ID}mm over {PUMP_SPIGOT_OD}mm spigot, "
          f"OD {SOCKET_OD}mm, insertion depth {SOCKET_DEPTH}mm")
    print(f"Through-bore: {BORE_DIA}mm dia, end to end")
    print(f"String ear: radius stays {SOCKET_OD_R}mm (matches the socket wall) the whole way up, "
          f"offset grows {EAR_OFFSET_START}->{EAR_OFFSET_MAX}mm over {EAR_GROWTH_H:.1f}mm at "
          f"{EAR_GROWTH_ANGLE_DEG:.1f} deg - no overhang, no narrow neck")
    print(f"1x {EAR_HOLE_DIA}mm hole through the crescent")
    print(f"Ear top at Z={EAR_TOP_Z:.1f}mm, socket rim at Z={Z_OPEN_END}mm "
          f"({EAR_SHORTER_AMOUNT:.1f}mm shorter)")
    print(f"Overall length: {Z_OPEN_END}mm")

    if EXPORT_STL:
        export_stl(adapter, "pump_adapter_v9.stl")

    if RENDER_IMAGES:
        center, size = compute_scene_bounds()
        render_angles(center, size)

    print("Done.")


if __name__ == "__main__":
    main()
