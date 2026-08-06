# Plain spacer block, sits between two sheets of plywood to hold them a
# fixed distance apart. Print 4 of these. Load is compression (the plywood
# sandwich bearing down on the spacer), which is FDM's strongest direction
# by a wide margin, so normal infill (~15-20%) is plenty -- no need for the
# procedural-mesh loft machinery the other parts in this project use, this
# is just a rounded box. Attaches with wood screws driven through the
# plywood into the walls -- no pilot holes modeled, screws self-tap into
# the shell/infill directly.
#
# Run headless:
#   blender --background --python spacer.py

import bpy
import bmesh
import math
import mathutils
import os

# ----------------------------
# CONFIG
# ----------------------------
BOX_LENGTH = 100.0   # mm -- X
BOX_WIDTH  =  65.0   # mm -- Y
BOX_HEIGHT =  50.0   # mm -- Z

CORNER_RADIUS   = 3.0   # mm -- rounded vertical edges, cosmetic/print-quality
CORNER_SEGMENTS = 4      # points per rounded corner

TRACK_LABEL = "pingis_spacer"

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

def make_spacer():
    profile = rounded_rect_profile(BOX_LENGTH, BOX_WIDTH, CORNER_RADIUS, CORNER_SEGMENTS)

    bm = bmesh.new()
    bottom_verts = [bm.verts.new((x, y, 0.0)) for x, y in profile]
    bottom_face = bm.faces.new(bottom_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    extruded = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])
    new_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0, 0, BOX_HEIGHT))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(TRACK_LABEL)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(TRACK_LABEL, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# ----------------------------
# RENDER (same convention as the other procedural-mesh scripts)
# ----------------------------
def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(200, -200, 400))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.angle = math.radians(5)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    bg.inputs["Strength"].default_value = 1.0

def setup_material(obj):
    mat = bpy.data.materials.new("render_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.65, 0.65, 0.70, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def point_camera(cam_obj, target_pos, up=mathutils.Vector((0, 1, 0))):
    direction = (target_pos - cam_obj.location).normalized()
    right = direction.cross(up).normalized()
    true_up = right.cross(direction).normalized()
    rot = mathutils.Matrix((right, true_up, -direction)).transposed().to_4x4()
    cam_obj.matrix_world = mathutils.Matrix.Translation(cam_obj.location) @ rot

RENDER_ANGLES = {   # same convention as the other procedural-mesh scripts
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

    center = mathutils.Vector((0.0, 0.0, BOX_HEIGHT / 2))
    D = max(BOX_LENGTH, BOX_WIDTH, BOX_HEIGHT) * 3.0

    bpy.ops.object.camera_add(location=(0, 0, 0))
    cam = bpy.context.active_object
    scene.camera = cam

    os.makedirs(render_dir, exist_ok=True)
    for label, direction in RENDER_ANGLES.items():
        dir_vec = mathutils.Vector(direction).normalized()
        cam.location = center + dir_vec * D
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

    spacer = make_spacer()

    if EXPORT_STL:
        export_stl(spacer, os.path.join(EXPORT_DIR, f"{TRACK_LABEL}.stl"))

    if EXPORT_RENDER:
        render_views(spacer, os.path.join(EXPORT_DIR, "renders"))

    print("Done.")

if __name__ == "__main__":
    main()
