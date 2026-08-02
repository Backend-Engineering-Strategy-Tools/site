"""
Pump-to-hose adapter (Blender bpy) - standalone, NOT terrain. V3.

Same part as pump_adapter_v2_tapered_shoulder.py, one change: the O-ring
groove is gone. The V1 print worked fine on the plain press fit alone
with no ring installed, so the groove was pure margin - dropping it also
shortens the part, since the plug no longer needs land on both sides of
a groove. The tapered shoulder (V2's fix for the rough overhang) now
starts right where the groove used to end, so the plug is just a plain
straight land from the tip to the taper.

Still one closed (r, z) profile revolved with bmesh.ops.spin - no
booleans - plus the same global bevel pass at the end.

Run: Blender -> Scripting workspace -> Open this file -> Alt+P
Or headless: blender --background --python pump_adapter_v3_no_oring.py
"""

import bpy
import bmesh
import math
import mathutils
import os

# ============================================================
# CONFIG (all mm)
# ============================================================

EXPORT_DIR = "/Users/mannil/Desktop/studio-m/TSONS/pump_adapter/output_v3"
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

SPIN_STEPS = 128  # circle segment count - smooth round bore/OD, not faceted

# --- Plug end (goes INTO the existing 18mm hole) ---
HOLE_ID = 18.0              # existing hole's diameter
PLUG_FIT_CLEARANCE = 0.4    # shrink plug OD below the hole so it slides in
PLUG_OD = HOLE_ID - PLUG_FIT_CLEARANCE   # 17.6mm land diameter
PLUG_INSERT_LEN = 7.0       # plain land, tip to taper start - matches where
                             # V2's O-ring groove used to end (4mm lead +
                             # 3mm groove width), now just kept as land

# --- Shoulder taper - straight cone from the plug land out to the socket
# OD, long enough to stay under a 45-degree overhang angle so FDM prints
# it with no support (see feedback_functional_parts_pipeline). ---
SHOULDER_TAPER_LEN = 6.0    # axial length of the taper

# --- Socket end (slides OVER the pump's 23mm spigot) ---
PUMP_SPIGOT_OD = 23.0
SOCKET_FIT_CLEARANCE = 0.3
SOCKET_ID = PUMP_SPIGOT_OD + SOCKET_FIT_CLEARANCE   # 23.3mm, slip fit over the spigot
SOCKET_WALL_T = 2.5
SOCKET_DEPTH = 8.0           # insertion depth for the pump spigot
FLOOR_WEB_T = 2.0            # solid wall between the socket floor and the through-bore

# --- Through-bore (flow passage, end to end) ---
BORE_DIA = 10.0

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

SHOULDER_TAPER_ANGLE_DEG = math.degrees(
    math.atan2(SOCKET_OD_R - PLUG_OD_R, SHOULDER_TAPER_LEN)
)  # off vertical - keep this <=45 so it prints without support

Z_TIP = 0.0
Z_SHOULDER_START = PLUG_INSERT_LEN
Z_SHOULDER_END = Z_SHOULDER_START + SHOULDER_TAPER_LEN
Z_SOCKET_FLOOR = Z_SHOULDER_END + FLOOR_WEB_T
Z_OPEN_END = Z_SHOULDER_END + SOCKET_LEN

assert BORE_R < PLUG_OD_R - 1.0, \
    "through-bore sits too close to the plug's outer wall - thin wall there"
assert BORE_R < SOCKET_ID_R, \
    "through-bore is bigger than the socket ID - shrink BORE_DIA"
assert SHOULDER_TAPER_ANGLE_DEG <= 45.0, \
    f"shoulder taper is {SHOULDER_TAPER_ANGLE_DEG:.1f} deg off vertical - lengthen SHOULDER_TAPER_LEN to keep it <=45"


# ============================================================
# HELPERS (shared conventions - see brazier/brazier.py, columns/columns.py)
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)


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


# ============================================================
# ADAPTER
# ============================================================

def build_adapter():
    """One continuous wall cross-section, traced as a single closed loop
    and revolved: tip face (outward) -> plug land -> tapered shoulder
    (self-supporting, not a sudden step) -> socket outer wall -> socket
    mouth face (inward) -> socket inner wall down to the floor -> floor
    web (inward) -> through-bore wall back down to the tip. No booleans -
    the whole part is this one spin."""
    profile = [
        (PLUG_OD_R, Z_TIP),
        (PLUG_OD_R, Z_SHOULDER_START),
        (SOCKET_OD_R, Z_SHOULDER_END),
        (SOCKET_OD_R, Z_OPEN_END),
        (SOCKET_ID_R, Z_OPEN_END),
        (SOCKET_ID_R, Z_SOCKET_FLOOR),
        (BORE_R, Z_SOCKET_FLOOR),
        (BORE_R, Z_TIP),
    ]
    profile.append(profile[0])  # close the loop back to the tip's outer edge

    obj = _spin_profile(profile, "pump_adapter_v3")
    apply_bevel(obj, BEVEL_WIDTH, BEVEL_SEGMENTS)
    return obj


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    clear_scene()

    adapter = build_adapter()

    print(f"Plug end: OD {PLUG_OD}mm into {HOLE_ID}mm hole, land length {PLUG_INSERT_LEN}mm (no O-ring groove)")
    print(f"Shoulder taper: {SHOULDER_TAPER_LEN}mm long, {SHOULDER_TAPER_ANGLE_DEG:.1f} deg off vertical "
          f"(<=45 prints without support)")
    print(f"Socket end: ID {SOCKET_ID}mm over {PUMP_SPIGOT_OD}mm spigot, "
          f"OD {SOCKET_OD}mm, insertion depth {SOCKET_DEPTH}mm")
    print(f"Through-bore: {BORE_DIA}mm dia, end to end")
    print(f"Overall length: {Z_OPEN_END}mm (was 28.0mm in V2, 29.0mm in V1)")

    if EXPORT_STL:
        export_stl(adapter, "pump_adapter_v3.stl")

    if RENDER_IMAGES:
        center, size = compute_scene_bounds()
        render_angles(center, size)

    print("Done.")


if __name__ == "__main__":
    main()
