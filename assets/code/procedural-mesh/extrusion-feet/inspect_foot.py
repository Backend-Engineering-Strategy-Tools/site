# Quick look at a downloaded reference part (E3X raised foot for 2040
# aluminum extrusion) — no procedural generation here, just import + render
# from the same camera/light convention as the other procedural-mesh
# projects, so the dual-track mounting geometry can actually be seen before
# deciding how to adapt it to a single-track extrusion.
#
# Run headless:
#   blender --background --python inspect_foot.py

import bpy
import math
import mathutils
import os

STL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "E3X_raised_foot.stl")
RENDER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
RENDER_RESOLUTION = (1600, 900)
RENDER_ANGLES = {   # same convention as scarf_slide.py / adapter.py / rack_support_brace.py
    "front": (0.0, -1.0, 0.15),
    "side": (1.0, -0.1, 0.15),
    "top": (0.001, -0.3, 1.0),
    "bottom": (0.001, -0.3, -1.0),
    "iso": (0.6, -1.0, 0.6),
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)


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
    center = mathutils.Vector((
        (min(xs) + max(xs)) / 2,
        (min(ys) + max(ys)) / 2,
        (min(zs) + max(zs)) / 2,
    ))
    size = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return center, size


def point_camera(cam_obj, target_pos, up=mathutils.Vector((0, 1, 0))):
    direction = (target_pos - cam_obj.location).normalized()
    right = direction.cross(up).normalized()
    true_up = right.cross(direction).normalized()
    rot = mathutils.Matrix((right, true_up, -direction)).transposed().to_4x4()
    cam_obj.matrix_world = mathutils.Matrix.Translation(cam_obj.location) @ rot


def setup_camera_and_light(center):
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    light_data = bpy.data.lights.new("RenderSun", type='SUN')
    light_data.energy = 3.0
    light_data.angle = math.radians(5)
    light_obj = bpy.data.objects.new("RenderSun", light_data)
    light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(35))
    bpy.context.collection.objects.link(light_obj)

    bpy.context.scene.camera = cam_obj
    return cam_obj


def render_angles(center, size, render_dir):
    os.makedirs(render_dir, exist_ok=True)
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
        point_camera(cam_obj, center)
        scene.render.filepath = os.path.join(render_dir, f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print(f"  rendered -> {scene.render.filepath}")


def apply_grey(obj):
    mat = bpy.data.materials.get("preview_grey")
    if mat is None:
        mat = bpy.data.materials.new("preview_grey")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.72, 1.0)
    obj.data.materials.append(mat)


def main():
    clear_scene()
    bpy.ops.wm.stl_import(filepath=STL_PATH)
    obj = bpy.context.selected_objects[0]
    apply_grey(obj)

    center, size = compute_scene_bounds()
    print(f"bounds: center={tuple(center)} size={size:.2f}mm")
    render_angles(center, size, RENDER_DIR)


if __name__ == "__main__":
    main()
