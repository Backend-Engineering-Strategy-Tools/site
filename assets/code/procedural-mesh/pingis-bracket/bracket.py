# Bracket that slides onto the wooden rail running under the table's end
# edge, and gives a flat face to screw a board to (the board carries the
# ball-catch net for a ping-pong practice robot). Two of these get printed,
# one per rail -- the table has two.
#
# Rail cross-section is a T/keyhole shape: a narrow neck against the apron,
# a 45-degree shoulder, then a flare with rounded bottom corners -- read off
# an actual end-on photo of the rail (not just the three headline
# measurements). The shoulder angle and corner radius aren't precisely
# measured, just estimated off that photo, so they're the parts most likely
# to need revisiting if the fit is off -- same lesson as the T-slot key on
# the extrusion feet project, where "looks about right" needed a second and
# third pass against real measurements before it actually fit.
#
# The bracket slides onto the rail lengthwise from an open end and stops
# against a closed end wall -- CHANNEL_LENGTH is deliberately less than
# BRACKET_LENGTH so there's a hard stop instead of needing to eyeball the
# position every time.
#
# No modeled fastener holes -- the board attaches with wood screws driven
# straight into the bracket's board-mounting face (self-tapping, no nut/head
# to capture). Infill density -- not geometry -- is what determines whether
# a screw actually holds, so that's handled at print/slicer time (a local
# 100%-infill modifier at each screw position) rather than in this model.
#
# Run headless:
#   blender --background --python bracket.py

import bpy
import bmesh
import math
import mathutils
import os

# ----------------------------
# CONFIG
# ----------------------------
# Rail profile (measured off the table's under-edge batten)
RAIL_NECK_WIDTH   = 19.0   # mm -- narrow part against the apron
RAIL_FLARE_WIDTH  = 32.0   # mm -- wider flared base
RAIL_HEIGHT       = 19.0   # mm -- apron to bottom of flare
RAIL_CLEARANCE    =  0.4   # mm -- added per side to both widths for a sliding fit

RAIL_FLARE_CORNER_RADIUS = 4.0   # mm -- rounding on the flare's bottom two
                                  # corners, estimated off the end-on photo
# Shoulder at 45 degrees -- same convention as the pedestal chamfer on the
# extrusion feet: height = run = half the width difference, not picked
# independently, so it comes out to exactly 45 automatically.
RAIL_SHOULDER_HEIGHT = (RAIL_FLARE_WIDTH - RAIL_NECK_WIDTH) / 2   # mm
RAIL_FLARE_HEIGHT = 7.0   # mm -- straight flare wall below the shoulder
RAIL_NECK_HEIGHT  = RAIL_HEIGHT - RAIL_FLARE_HEIGHT - RAIL_SHOULDER_HEIGHT

CUTTER_MARGIN = 3.0   # mm -- cutters extend this far past the surfaces they
                       # cut through, so boolean differences don't leave a
                       # coplanar face (silently fails to cut cleanly)

# TEST_PIECE swaps the full bracket for a short block containing just the
# channel -- open at both ends, no bolt holes -- fast to print so the rail
# fit can be checked before committing to a full print.
TEST_PIECE  = False
TEST_LENGTH =  10.0   # mm -- the channel's cross-section is constant along
                       # its length, so a thin slice checks the fit just as
                       # well as a long one -- shorter just prints faster
TEST_WALL   =   5.0   # mm -- material around the channel profile

# Bracket body -- WIDTH is generous (100mm, not just flare+wall) specifically
# so the 4 bolts get real spread for anti-rotation leverage; DEPTH only
# needs to clear the rail height plus the bolt pockets, so it's shallow
if TEST_PIECE:
    BRACKET_LENGTH = TEST_LENGTH
    BRACKET_WIDTH  = RAIL_FLARE_WIDTH + 2 * RAIL_CLEARANCE + 2 * TEST_WALL
    BRACKET_DEPTH  = RAIL_HEIGHT + TEST_WALL
    CHANNEL_LENGTH = BRACKET_LENGTH + 2 * CUTTER_MARGIN   # open both ends
else:
    BRACKET_LENGTH = 100.0   # mm -- X, along the rail (slide-on axis)
    BRACKET_WIDTH  = 100.0   # mm -- Y, the flat mounting face's width
    BRACKET_DEPTH  =  40.0   # mm -- Z, rail-contact face (top) to board-mount face (bottom)
    CHANNEL_LENGTH =  90.0   # mm -- open at X=0 (slide-on end), closed the
                              # remaining (BRACKET_LENGTH - CHANNEL_LENGTH) as
                              # a hard end-stop the rail butts up against

# No modeled fastener holes -- board attaches with wood screws driven
# directly into the bracket (self-tapping), sized/placed at print time via
# a slicer infill modifier rather than anything baked into the STL. An STL
# is just a boundary surface; infill density is a slicer-time decision, not
# a modeling one, so a pilot hole here wouldn't actually address screw
# holding strength anyway -- and a narrow pre-drilled hole is harder to hit
# blind through the board than just aiming a screw into a wide solid zone.

TRACK_LABEL = "pingis_bracket_test" if TEST_PIECE else "pingis_bracket"

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
def extrude_profile_along_x(name, points_yz, x_start, x_end):
    """Solid built by extruding a closed (y, z) polygon along X from x_start
    to x_end -- for a constant cross-section swept lengthwise, which is what
    both the bracket's outer box and the rail channel cutter are."""
    bm = bmesh.new()
    start_verts = [bm.verts.new((x_start, y, z)) for y, z in points_yz]
    start_face = bm.faces.new(start_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    extruded = bmesh.ops.extrude_face_region(bm, geom=[start_face])
    new_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(x_end - x_start, 0, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

CORNER_SEGMENTS = 4   # points per rounded flare corner

def rail_channel_profile():
    """(y, z) polygon for the rail's T/keyhole cross-section, plus
    clearance, in LOCAL coordinates where z=0 is the bottom of the flare
    (a blind pocket floor -- not cut through, so no CUTTER_MARGIN there)
    and z=RAIL_HEIGHT is the apron-facing top (open through the bracket's
    top face, so extended by CUTTER_MARGIN). Bottom-right/left corners are
    rounded by RAIL_FLARE_CORNER_RADIUS; the shoulder is a straight
    45-degree chamfer, not rounded -- both are estimates off the end-on
    photo, see header note."""
    neck_hw  = (RAIL_NECK_WIDTH + 2 * RAIL_CLEARANCE) / 2
    flare_hw = (RAIL_FLARE_WIDTH + 2 * RAIL_CLEARANCE) / 2
    r = RAIL_FLARE_CORNER_RADIUS
    shoulder_top = RAIL_FLARE_HEIGHT + RAIL_SHOULDER_HEIGHT
    top = RAIL_HEIGHT + CUTTER_MARGIN

    # Right corner: arc center (flare_hw - r, r), sweeping from straight-down
    # (tangent to the bottom edge) to straight-out (tangent to the flare wall)
    right_arc = []
    for i in range(CORNER_SEGMENTS + 1):
        a = math.radians(-90 + 90 * i / CORNER_SEGMENTS)
        right_arc.append((flare_hw - r + r * math.cos(a), r + r * math.sin(a)))

    # Left corner is the right corner mirrored and traversed the other way,
    # so the whole loop stays a consistent winding order
    left_arc = [(-y, z) for y, z in reversed(right_arc)]

    # right_arc[0] and left_arc[-1] are both already at z=0 (the arcs'
    # bottom tangent points) -- the face loop closes the gap between them
    # automatically, which is exactly the straight bottom edge.
    return (
        right_arc
        + [(flare_hw, RAIL_FLARE_HEIGHT), (neck_hw, shoulder_top), (neck_hw, top),
           (-neck_hw, top), (-neck_hw, shoulder_top), (-flare_hw, RAIL_FLARE_HEIGHT)]
        + left_arc
    )

def make_bracket_body():
    hw = BRACKET_WIDTH / 2
    points = [(-hw, 0), (hw, 0), (hw, BRACKET_DEPTH), (-hw, BRACKET_DEPTH)]
    return extrude_profile_along_x(TRACK_LABEL, points, 0.0, BRACKET_LENGTH)

def make_channel_cutter():
    profile = rail_channel_profile()
    # local z=0 (bottom of flare) sits RAIL_HEIGHT below the bracket's top
    # (rail-contact) face, i.e. at global z = BRACKET_DEPTH - RAIL_HEIGHT
    z_offset = BRACKET_DEPTH - RAIL_HEIGHT
    shifted = [(y, z + z_offset) for y, z in profile]
    # extend past x=0 so the open end actually cuts through that face
    cutter = extrude_profile_along_x("channel_cutter", shifted,
                                      -CUTTER_MARGIN, CHANNEL_LENGTH)
    return cutter

# ----------------------------
# RENDER (same convention as the other procedural-mesh scripts)
# ----------------------------
def setup_lighting():
    bpy.ops.object.light_add(type='SUN', location=(200, -200, 400))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.data.angle = math.radians(5)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    # Flat ambient fill so faces angled away from the sun (e.g. the
    # underside, in the "bottom" view) don't render pure black -- this part
    # specifically needs the underside's bolt pockets to actually be
    # visible, which a single directional light can't guarantee
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

    center = mathutils.Vector((BRACKET_LENGTH / 2, 0.0, BRACKET_DEPTH / 2))
    D = max(BRACKET_LENGTH, BRACKET_WIDTH, BRACKET_DEPTH) * 3.0

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
def recalc_normals(obj):
    # Boolean DIFFERENCE ops can leave inconsistent face normals on the cut
    # surfaces even when the mesh is otherwise a valid manifold solid --
    # same class of silent issue as the extrusion-feet project's bevel bug,
    # here showing up as faces rendering black (backface, unlit) instead of
    # a visibly corrupted surface.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()

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

    bracket = make_bracket_body()

    channel = make_channel_cutter()
    boolean(bracket, channel, 'DIFFERENCE')

    recalc_normals(bracket)

    if EXPORT_STL:
        export_stl(bracket, os.path.join(EXPORT_DIR, f"{TRACK_LABEL}.stl"))

    if EXPORT_RENDER:
        render_views(bracket, os.path.join(EXPORT_DIR, f"renders_{TRACK_LABEL}"))

    print("Done.")

if __name__ == "__main__":
    main()
