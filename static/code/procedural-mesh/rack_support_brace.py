# Hole Box v1
# Flat 200×150×8mm plate with 3 rows of 6mm through-holes.
# Column spacing alternates: 22mm (within pair), 20mm (between pairs).
# Row layout: 1 row — 2 blank slots — 2 rows.
# Paste into the Blender Script Editor and run (Alt+P).

import bpy
import bmesh
import math
import os
import mathutils

# ----------------------------
# CONFIG
# ----------------------------
PLATE_X       = 220.0   # mm — length (hole axis) — change to 220.0 for larger bed
PLATE_Y       = 150.0   # mm — width
PLATE_Z       =   8.0   # mm — thickness

HOLE_DIAM     =   7.0   # mm — hole diameter
# Column spacing pattern — repeats along X: within-pair gap, between-pair gap
PAIR_GAP      =  22.0   # mm CC within a pair
BETWEEN_GAP   =  23.0   # mm CC between pairs
N_COLS        =  10     # fixed number of holes per row
ROW_SPACING   =  20.0   # mm CC between slots
N_ROW_SLOTS   =   7     # total slot positions (including blanks)
SKIP_ROWS     = [2, 3, 5]  # zero-indexed slot numbers to leave empty
HOLE_SEGMENTS =  32     # cylinder resolution

# Text engraving — recessed into top face, never raised
ENGRAVE_DEPTH =  1.0    # mm deep (leaves 7mm of material on an 8mm plate)
TEXT_LINE1    = "B.E.S.T"
TEXT_LINE2    = "support brace v7  2026"
TEXT_SIZE1    =  8.0    # mm — glyph height line 1
TEXT_SIZE2    =  4.5    # mm — glyph height line 2
TEXT_LINE_GAP =  8.0    # mm — centre-to-centre between lines
TEXT_Y        = -10.0   # mm — vertical centre of block (sits in the wide row gap)

EXPORT_STL    = False
EXPORT_RENDER = True
EXPORT_DIR    = "//stl_output"   # // = relative to .blend file; or use an absolute path
RENDER_RES_X  = 1920
RENDER_RES_Y  = 1080

# ----------------------------
# UTILITIES
# ----------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)

def compute_hole_positions():
    """
    Builds column positions using alternating PAIR_GAP / BETWEEN_GAP spacing,
    then centres the whole grid on the plate.  Rows use uniform ROW_SPACING.
    """
    # --- columns (X axis) ---
    # Fixed N_COLS holes with alternating PAIR_GAP / BETWEEN_GAP spacing, centred on plate.
    gaps = [PAIR_GAP, BETWEEN_GAP]
    col_offsets = [0.0]
    for i in range(1, N_COLS):
        col_offsets.append(col_offsets[-1] + gaps[(i - 1) % 2])

    col_span = col_offsets[-1] - col_offsets[0]
    x_origin = -col_span / 2   # centre on plate

    # --- rows (Y axis) ---
    skip_set = set(SKIP_ROWS)
    row_span = (N_ROW_SLOTS - 1) * ROW_SPACING
    y_origin = -row_span / 2

    row_offsets = [
        y_origin + s * ROW_SPACING
        for s in range(N_ROW_SLOTS)
        if s not in skip_set
    ]

    positions = [
        (x_origin + cx, ry)
        for ry in row_offsets
        for cx in col_offsets
    ]
    return positions

# ----------------------------
# GEOMETRY
# ----------------------------
def make_plate():
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = "HoleBox_plate"
    obj.dimensions = (PLATE_X, PLATE_Y, PLATE_Z)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def make_cutter(positions):
    """Builds one mesh with all hole cylinders joined — one boolean cut."""
    radius = HOLE_DIAM / 2
    depth  = PLATE_Z + 2   # +1mm top and bottom for clean cut faces

    bpy.ops.object.select_all(action='DESELECT')
    cyl_objects = []
    for (x, y) in positions:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=HOLE_SEGMENTS,
            radius=radius,
            depth=depth,
            location=(x, y, 0),
        )
        cyl_objects.append(bpy.context.active_object)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in cyl_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = cyl_objects[0]
    bpy.ops.object.join()

    cutter = bpy.context.active_object
    cutter.name = "HoleBox_cutter"
    return cutter

def cut_holes(plate, cutter):
    # Hide cutter so it doesn't show during processing
    cutter.hide_set(True)

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = plate
    plate.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')   # modifier_apply requires Object mode

    mod = plate.modifiers.new(name="Holes", type='BOOLEAN')
    mod.operation  = 'DIFFERENCE'
    mod.object     = cutter
    mod.solver     = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="Holes")

    bpy.data.objects.remove(cutter, do_unlink=True)

# ----------------------------
# TEXT ENGRAVING
# ----------------------------
def engrave_text(plate):
    # Place text below the top surface by ENGRAVE_DEPTH, extrude upward through it.
    # Boolean difference then cuts recessed letters into the face.
    z = PLATE_Z / 2 - ENGRAVE_DEPTH

    def make_line(body, size, y):
        bpy.ops.object.text_add(location=(0, y, z))
        obj = bpy.context.active_object
        obj.data.body    = body
        obj.data.size    = size
        obj.data.align_x = 'CENTER'
        obj.data.align_y = 'CENTER'
        obj.data.extrude = ENGRAVE_DEPTH + 0.5   # +0.5 ensures cutter clears top face
        bpy.ops.object.convert(target='MESH')
        return obj

    t1 = make_line(TEXT_LINE1, TEXT_SIZE1, TEXT_Y + TEXT_LINE_GAP / 2)
    t2 = make_line(TEXT_LINE2, TEXT_SIZE2, TEXT_Y - TEXT_LINE_GAP / 2)

    bpy.ops.object.select_all(action='DESELECT')
    t1.select_set(True)
    t2.select_set(True)
    bpy.context.view_layer.objects.active = t1
    bpy.ops.object.join()
    cutter = bpy.context.active_object
    cutter.name = "text_cutter"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = plate
    plate.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = plate.modifiers.new(name="TextEngrave", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object    = cutter
    mod.solver    = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="TextEngrave")

    bpy.data.objects.remove(cutter, do_unlink=True)
    print(f"  engraved: '{TEXT_LINE1}' / '{TEXT_LINE2}' ({ENGRAVE_DEPTH}mm deep)")

# ----------------------------
# RENDER
# ----------------------------
def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(200, -200, 400))
    sun = bpy.context.active_object
    sun.name = "render_sun"
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

def setup_material(obj):
    mat = bpy.data.materials.new("render_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.65, 0.65, 0.70, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Metallic"].default_value = 0.1
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def make_camera(name, location, target):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam

def render_views(obj, export_dir):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = RENDER_RES_X
    scene.render.resolution_y = RENDER_RES_Y
    scene.render.image_settings.file_format = 'PNG'

    setup_lighting()
    setup_material(obj)

    cx, cy, cz = 0.0, 0.0, PLATE_Z / 2        # aim at plate centre
    D = max(PLATE_X, PLATE_Y) * 2.8            # camera distance

    views = [
        ("top",   ( 0,    0,    D        )),
        ("front", ( 0,   -D,    cz       )),
        ("side",  (-D,    0,    cz       )),
        ("iso",   (-D*.6, -D*.6, D * .5  )),
    ]

    render_dir = os.path.join(export_dir, "renders")
    os.makedirs(render_dir, exist_ok=True)

    for label, loc in views:
        cam = make_camera(f"cam_{label}", loc, (cx, cy, cz))
        scene.camera = cam
        out = os.path.join(render_dir, f"{obj.name}_{label}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(cam, do_unlink=True)
        print(f"  rendered {label} → {out}")

    print(f"  renders → {render_dir}/")

# ----------------------------
# EXPORT
# ----------------------------
def export_stl(obj):
    out  = bpy.path.abspath(EXPORT_DIR)
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{obj.name}.stl")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"  exported → {path}")

# ----------------------------
# MAIN
# ----------------------------
clear_scene()

positions = compute_hole_positions()
n_rows = N_ROW_SLOTS - len(SKIP_ROWS)
print(f"Hole grid: {n_rows} rows × {N_COLS} cols = {len(positions)} holes  (slots: {N_ROW_SLOTS}, skipped: {SKIP_ROWS})")
print(f"Column spacing pattern: {PAIR_GAP}mm / {BETWEEN_GAP}mm (repeating)")

plate  = make_plate()
cutter = make_cutter(positions)
cut_holes(plate, cutter)
engrave_text(plate)

plate.name = f"rack_support_brace_{int(PLATE_X)}x{int(PLATE_Y)}"

out_dir = bpy.path.abspath(EXPORT_DIR)

if EXPORT_STL:
    export_stl(plate)

if EXPORT_RENDER:
    render_views(plate, out_dir)

print("Done.")
