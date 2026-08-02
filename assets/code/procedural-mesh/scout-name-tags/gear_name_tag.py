# Gear Name Tag v4
# Stylized cog-shaped tag, ~42mm across, 4mm thick, keyring hole near the top edge.
# Two-sided: FRONT is the cog ring + fleur-de-lis only (matches the Mölndals
# Scoutkår emblem), BACK carries the text ("Mölndal" + name, line-broken to fit).
# Built for genuine 4-color multi-material printing (e.g. Anycubic Kobra X / ACE
# Gen2, Bambu AMS, etc.): the body has a shallow recess on each face for its
# element, and each element is exported as its own separate, exactly-fitting
# STL insert. Import body.stl + all element STLs together into your slicer
# (they share the same coordinate space, so they align automatically), then
# assign a different filament/color to each imported object.
#
# Run headless per name:
#   blender --background --python gear_name_tag.py -- "Ivan" "Nilsson"

import bpy
import bmesh
import json
import math
import mathutils
import os
import sys

# ----------------------------
# CONFIG
# ----------------------------
OUTER_R       = 21.0   # mm — tip radius of gear teeth
INNER_R       = 18.0   # mm — root radius (valleys between teeth)
# Tooth count taken from the actual Mölndals Scoutkår cog (FFT on the radial
# profile of input/scout/Mölndal_Nummer.3mf): 12 teeth, dominant harmonic
# magnitude ~3x the next candidate. Profile is castellated/square — flat top,
# straight RADIAL step down to a flat root — matching the reference emblem's
# blocky cog, not a diagonal ramp or a rounded scallop (both tried first,
# both wrong). Root width is implicit: whatever's left after TOOTH_FRAC.
N_TEETH       = 12
TOOTH_FRAC    = 0.5    # flat-tip fraction of one tooth's angular period — ring
WHITE_TOOTH_FRAC = 0.28  # narrower teeth for the white cog — same N_TEETH
                          # positions, thinner, so more red shows around them
THICKNESS     = 4.0    # mm — body thickness

HOLE_DIAM     = 4.0    # mm — keyring hole
HOLE_R        = 13.0   # mm — hole centre distance from origin. Pulled back in
                        # from 16 now that the angle is a tooth valley again
                        # (white cog's root there is 16.5, so 13+diam/2=15
                        # keeps a safe 1.5mm margin).
HOLE_ANGLE_DEG = 15     # one tooth-valley down from 45deg — 45 put the hole
                        # right against the MÖLNDAL text. Still a valley
                        # (multiple of 30deg +/- half a segment), just lower.

BEVEL_WIDTH   = 0.25   # mm — just breaks the raw edge, kept small so corners read as square
BEVEL_SEGMENTS = 1

INSERT_DEPTH  = 0.6    # mm — recess depth / insert thickness

# Body is two full-thickness pieces: RING (red) is the complete, unbroken
# gear solid — full teeth, full side walls — with the WHITE_COG's footprint
# cut out of it. WHITE_COG is the same castellated shape inset by
# TEETH_INLAY_INSET, kept as one piece that holds the keyring hole, the front
# logo recess, and the back-face text recess — no separate hub circle.
# Tradeoff: white_cog's own tooth side-walls are exposed at the inset
# boundary (a shallow, front-face-only version avoided that but was too
# fragile to print/handle as its own piece — full thickness won out).
TEETH_INLAY_INSET = 1.5   # mm — how far the white cog sits inside the outer cog outline

# FRONT face — cog ring (red) + fleur-de-lis on the disc (blue), matching the
# Mölndals Scoutkår emblem. No text on this face.
# Traced from input/stamp_french_lily.png (WOSM-style fleur-de-lis) via
# marching-squares contour extraction — 15 independent pieces (no dilation
# to merge them: that smeared the fine swirl detail into a blob), baked to
# an 18mm bounding box. See assets/code/procedural-mesh/scout-name-tags/
# lily_stamp.json. LOGO_SIZE is a plain multiplier on that baked scale.
LOGO_STAMP    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lily_stamp.json")
LOGO_SIZE     = 1.6
LOGO_Y        = 0.0    # centered — front face has nothing else on it

# BACK face (disc) — "MÖLNDAL" + name, all caps for legibility (it's a name
# tag). TEXT_FONT is a bold condensed face to echo the wordmark's look (incl.
# the dotted, blocky Ö) — DIN Condensed Bold is the closest match available
# locally; not the actual brand font.
TEXT_FONT     = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"

TOP_TEXT      = "MÖLNDAL"
TOP_SIZE      = 8.0
TOP_Y         = 6.0

# Phone sits in the middle row (Y near 0) — the circle is widest there, and
# the phone number is the longest string, so it gets the most room.
PHONE_SIZE    = 8.0
PHONE_Y       = 0.0

NAME_SIZE     = 8.0    # first + surname, now two independent lines (not one
                        # line-broken block) so their Y can be set explicitly
                        # for uniform pitch with the rows above
FIRSTNAME_Y   = -6.0
SURNAME_Y     = -12.0
# Pitch is uniform: MÖLNDAL(+6) -> phone(0) -> first name(-6) -> surname(-12).
# 8mm pitch (matching font size) put surname past the white cog's safe width
# and it clipped into the teeth — 6mm is a compromise that still fits.
# 8mm between every consecutive row.

MAX_TEXT_WIDTH = 34.0   # mm — auto-shrink a line if its rendered width exceeds this

EXPORT_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "name_tags")
EXPORT_COMBINED = False  # skip combined.stl while iterating on per-part geometry

RENDER_IMAGES = True
RENDER_RESOLUTION = (1600, 900)
RENDER_ANGLES = {   # same convention as adapter.py / rack_support_brace.py
    "front": (0.0, -1.0, 0.15),
    "side": (1.0, -0.1, 0.15),
    "top": (0.001, -0.3, 1.0),
    "bottom": (0.001, -0.3, -1.0),
    "iso": (0.6, -1.0, 0.6),
}

COLORS = {
    "red": (0.8, 0.05, 0.05, 1.0),
    "blue": (0.05, 0.25, 0.8, 1.0),
    "white": (0.95, 0.95, 0.95, 1.0),
    "black": (0.02, 0.02, 0.02, 1.0),
}
ELEMENT_COLORS = {   # render-only — STL has no color, this just makes previews readable
    "ring": COLORS["red"],         # complete gear solid — full teeth, full side walls
    "hub": COLORS["white"],        # hub + teeth_inlay joined — cog-shaped white piece
    "logo": COLORS["blue"],        # fleur-de-lis
    "molndal": COLORS["black"],    # text
    "firstname": COLORS["black"],  # same filament slot as molndal
    "surname": COLORS["black"],    # same filament slot as molndal
    "phone": COLORS["black"],      # optional row — same filament slot as molndal/name
}

# ----------------------------
# UTILITIES
# ----------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)

def recalc_normals(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

def apply_color(obj, name, rgba):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = rgba
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def force_manifold(obj, voxel_size=0.12):
    """Font-derived meshes (esp. symbol glyphs like the fleur-de-lis) can come out
    non-manifold, which silently corrupts Blender's EXACT boolean solver instead of
    failing loudly. Voxel remeshing guarantees clean, watertight geometry."""
    mod = obj.modifiers.new(name="ForceManifold", type='REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = voxel_size
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="ForceManifold")

# ----------------------------
# GEOMETRY — body (ring + disc)
# ----------------------------
def _build_gear_solid(outer_r, inner_r, tooth_frac=TOOTH_FRAC, bevel_edges=True):
    """Castellated/square teeth — flat tip, a straight RADIAL step down to a
    flat root (not a diagonal ramp), like the reference emblem's cog. Per
    tooth: flat top (tip_l->tip_r), radial step at tip_r's angle (outer_r ->
    inner_r), flat root over to the next tooth's tip_l angle. The step back
    up happens implicitly between this tooth's last vertex and the next
    tooth's first — same angle, so it's radial too. Takes radii and
    tooth_frac as params so the white cog can use narrower teeth than ring
    while staying centered on the same N_TEETH angular positions."""
    bm = bmesh.new()
    verts = []
    segment = 2 * math.pi / N_TEETH
    tip_half = segment * tooth_frac / 2
    for i in range(N_TEETH):
        center = segment * i
        a_tip_l = center - tip_half
        a_tip_r = center + tip_half
        a_next_tip_l = center + segment - tip_half
        verts.append(bm.verts.new((outer_r * math.cos(a_tip_l), outer_r * math.sin(a_tip_l), 0)))
        verts.append(bm.verts.new((outer_r * math.cos(a_tip_r), outer_r * math.sin(a_tip_r), 0)))
        verts.append(bm.verts.new((inner_r * math.cos(a_tip_r), inner_r * math.sin(a_tip_r), 0)))
        verts.append(bm.verts.new((inner_r * math.cos(a_next_tip_l), inner_r * math.sin(a_next_tip_l), 0)))

    face = bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    extruded_verts = [v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, THICKNESS), verts=extruded_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("gear_tag")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("gear_tag", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location.z = -THICKNESS / 2   # centre thickness on z=0 -> body spans [-T/2, +T/2]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True)

    if bevel_edges:
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = BEVEL_WIDTH
        bevel.segments = BEVEL_SEGMENTS
        bevel.limit_method = 'ANGLE'
        bevel.angle_limit = math.radians(20)
        bpy.ops.object.modifier_apply(modifier="Bevel")

    return obj

def _boolean_diff(obj, cutter_obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    mod = obj.modifiers.new(name="Diff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter_obj
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="Diff")
    bpy.data.objects.remove(cutter_obj, do_unlink=True)

def build_ring_and_white():
    """Two full-thickness pieces: RING (red) is the complete, unbroken gear
    solid — full teeth, full side walls, nothing cut out of it except the
    inset white cog's footprint. WHITE_COG is the same castellated shape
    inset by TEETH_INLAY_INSET, kept as ONE piece that does everything the
    old separate "hub" used to (keyring hole, front logo recess, back-face
    text recess) — no separate circular hub needed, since the inset cog's
    own root is already big enough to hold that central area.

    Tradeoff, chosen deliberately over a shallow front-only inlay (tried
    first): white_cog's own tooth side-walls are exposed at the inset
    boundary — a shallow (0.6mm) version avoided that but was too fragile to
    print/handle as its own piece.

    Does NOT cut the keyring hole — that happens last, in build(), after
    every other boolean on white_cog. Cutting the hole earlier has bitten us
    twice already (it vanished when cut before the teeth-inlay recess; a
    hole-shaped gap in a duplicate-before-cutting cutter left a solid plug
    in ring) — the EXACT solver seems to get confused when the hole
    interacts with whatever boolean comes after it, so it's safest as the
    final operation, full stop."""
    ring = _build_gear_solid(OUTER_R, INNER_R)
    ring.name = "ring"

    white = _build_gear_solid(OUTER_R - TEETH_INLAY_INSET, INNER_R - TEETH_INLAY_INSET,
                               tooth_frac=WHITE_TOOTH_FRAC, bevel_edges=False)
    white.name = "white_cog"

    # duplicate for ring's cutter BEFORE cutting the hole — otherwise the
    # cutter has a hole-shaped gap too, and subtracting a shape with a gap
    # leaves ring's original material sitting there untouched (showed up as
    # a solid red plug exactly where the hole should be). Cut the hole into
    # white only, after; ring has no material in that area regardless once
    # properly subtracted.
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = white
    white.select_set(True)
    bpy.ops.object.duplicate()
    cutter = bpy.context.active_object
    cutter.name = "white_cog_cutter"
    cutter.scale.z = (THICKNESS + 2) / THICKNESS
    bpy.ops.object.transform_apply(scale=True)

    _boolean_diff(ring, cutter)
    cut_hole(white)

    return ring, white

def cut_hole(plate):
    angle = math.radians(HOLE_ANGLE_DEG)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=HOLE_DIAM / 2, depth=THICKNESS + 2,
        location=(HOLE_R * math.cos(angle), HOLE_R * math.sin(angle), 0),
    )
    cutter = bpy.context.active_object
    cutter.name = "hole_cutter"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = plate
    plate.select_set(True)

    mod = plate.modifiers.new(name="Hole", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="Hole")

    bpy.data.objects.remove(cutter, do_unlink=True)

# ----------------------------
# TEXT / LOGO elements
# ----------------------------
def make_text_obj(body, size, y, depth, extra_top=0.0, font_path=None, face='top'):
    """Text mesh recessed into either face. For 'top' it spans
    [face_z-depth, face_z+extra_top]; for 'bottom', [face_z-extra_top, face_z+depth]
    — extra_top=0 -> flush insert, extra_top>0 -> oversized cutter that pokes
    out past the surface for a clean boolean subtraction."""
    face_z = THICKNESS / 2 if face == 'top' else -THICKNESS / 2
    if face == 'top':
        lo, hi = face_z - depth, face_z + extra_top
    else:
        lo, hi = face_z - extra_top, face_z + depth
    center_z = (lo + hi) / 2
    half_thick = (hi - lo) / 2

    bpy.ops.object.text_add(location=(0, y, center_z))
    obj = bpy.context.active_object
    obj.data.body = body
    obj.data.size = size
    obj.data.align_x = 'CENTER'
    obj.data.align_y = 'CENTER'
    obj.data.extrude = half_thick
    if font_path:
        obj.data.font = bpy.data.fonts.load(font_path)
    bpy.ops.object.convert(target='MESH')

    if face == 'bottom':
        # back-face text needs mirroring on X — otherwise it reads backwards
        # when the tag is physically flipped left-right to view the back.
        obj.scale.x = -1
        bpy.ops.object.transform_apply(scale=True)

    width = obj.dimensions.x
    if width > MAX_TEXT_WIDTH:
        scale = MAX_TEXT_WIDTH / width
        obj.scale.x = scale
        obj.scale.y = scale
        bpy.ops.object.transform_apply(scale=True)

    recalc_normals(obj)
    force_manifold(obj)
    return obj

def _build_polygon_solid(points_2d, z_lo, z_hi):
    """Extrude an arbitrary closed 2D point loop (no holes) into a solid
    spanning z in [z_lo, z_hi] — same bmesh spin-and-extrude style as
    _build_gear_solid, just for a traced silhouette loop instead of a
    parametric tooth profile."""
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z_lo)) for x, y in points_2d]
    face = bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    extruded_verts = [v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, z_hi - z_lo), verts=extruded_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("stamp_piece")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("stamp_piece", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def make_stamp_obj(stamp_path, size, y, depth, extra_top=0.0, face='top'):
    """Insert built from a traced silhouette (independent pieces, see
    LOGO_STAMP's comment) instead of a font glyph — same recess/insert
    depth convention as make_text_obj. `size` multiplies the JSON's
    already-baked-to-mm coordinates; `y` is a plain Y offset (no rotation/
    mirroring needed — the stamp is only ever used on the front)."""
    with open(stamp_path) as f:
        pieces = json.load(f)["pieces"]

    face_z = THICKNESS / 2 if face == 'top' else -THICKNESS / 2
    if face == 'top':
        lo, hi = face_z - depth, face_z + extra_top
    else:
        lo, hi = face_z - extra_top, face_z + depth

    objs = [
        _build_polygon_solid([(x * size, py * size + y) for x, py in piece], lo, hi)
        for piece in pieces
    ]

    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = objs[0]

    recalc_normals(obj)
    force_manifold(obj)
    return obj

ELEMENTS = [
    # front: cog + lily only, no text
    # back: "Mölndal" + name
    ("molndal", TOP_TEXT,   TOP_SIZE,  TOP_Y,  TEXT_FONT,  'bottom'),
]
# name added per-build since it depends on the person

def recess_and_export_elements(plate, first_name, surname, phone=None):
    text_elements = ELEMENTS + [
        ("firstname", first_name.upper(), NAME_SIZE, FIRSTNAME_Y, TEXT_FONT, 'bottom'),
        ("surname", surname.upper(), NAME_SIZE, SURNAME_Y, TEXT_FONT, 'bottom'),
    ]
    if phone:
        text_elements = text_elements + [
            ("phone", phone, PHONE_SIZE, PHONE_Y, TEXT_FONT, 'bottom'),
        ]

    def build_all(extra_top):
        objs = {"logo": make_stamp_obj(LOGO_STAMP, LOGO_SIZE, LOGO_Y, INSERT_DEPTH, extra_top=extra_top, face='top')}
        for key, body, size, y, font, face in text_elements:
            objs[key] = make_text_obj(body, size, y, INSERT_DEPTH, extra_top=extra_top, font_path=font, face=face)
        return objs

    cutters = build_all(extra_top=0.6)

    bpy.ops.object.select_all(action='DESELECT')
    for c in cutters.values():
        c.select_set(True)
    bpy.context.view_layer.objects.active = cutters["logo"]
    bpy.ops.object.join()
    cutter_union = bpy.context.active_object
    cutter_union.name = "recess_cutter"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = plate
    plate.select_set(True)
    mod = plate.modifiers.new(name="Recess", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter_union
    mod.solver = 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="Recess")
    bpy.data.objects.remove(cutter_union, do_unlink=True)

    return build_all(extra_top=0.0)

# ----------------------------
# EXPORT
# ----------------------------
def export_stl(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"  exported -> {path}")

# ----------------------------
# RENDER (same convention as adapter.py / rack_support_brace.py)
# ----------------------------
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

def point_camera(cam_obj, target_pos, up=mathutils.Vector((0, 1, 0))):
    """Explicit look-at matrix — NOT a TRACK_TO constraint. TRACK_TO's
    up_axis='UP_Y' produces a mirrored chirality specifically when the camera
    sits below the target looking up (confirmed empirically: same up_axis,
    different result vs. this direct construction). Two-sided parts with
    back-face text need the below-camera view to actually match a physical
    flip, so this script builds the camera matrix directly instead."""
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
    light_data.angle = math.radians(5)   # soften shadows — hard sun shadows alias into
                                          # a dashed pattern on shallow (0.6mm) front-face inserts
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

# ----------------------------
# MAIN
# ----------------------------
def build(first_name, surname, phone=None):
    clear_scene()
    if phone:
        phone = phone.replace(" ", "")
    ring, white = build_ring_and_white()
    inserts = recess_and_export_elements(white, first_name, surname, phone=phone)
    cut_hole(white)   # last, always — see build_ring_and_white's docstring
    cut_hole(inserts["logo"])   # the hole's position can overlap the logo insert's
                                 # footprint — punch it there too so nothing blocks
                                 # a keyring passing through

    out_dir = os.path.join(EXPORT_DIR, f"{first_name}_{surname}")
    export_stl(ring, os.path.join(out_dir, "ring.stl"))
    export_stl(white, os.path.join(out_dir, "white_cog.stl"))
    export_stl(inserts["logo"], os.path.join(out_dir, "logo.stl"))
    export_stl(inserts["molndal"], os.path.join(out_dir, "molndal.stl"))
    export_stl(inserts["firstname"], os.path.join(out_dir, "firstname.stl"))
    export_stl(inserts["surname"], os.path.join(out_dir, "surname.stl"))
    if "phone" in inserts:
        export_stl(inserts["phone"], os.path.join(out_dir, "phone.stl"))

    # combined multi-shell STL — import THIS as a single object so the slicer
    # doesn't independently re-center each part and destroy the alignment.
    # Assign filaments per disconnected shell ("Split to Objects" / per-island
    # coloring) once it's loaded — molndal+name share one slot (black), so
    # 5 shells still print in 4 colors.
    # Disabled for now while iterating on the individual pieces — turn back
    # on with EXPORT_COMBINED once the per-part geometry is settled.
    if EXPORT_COMBINED:
        combined_path = os.path.join(out_dir, "combined.stl")
        os.makedirs(out_dir, exist_ok=True)
        bpy.ops.object.select_all(action='DESELECT')
        ring.select_set(True)
        white.select_set(True)
        for ins in inserts.values():
            ins.select_set(True)
        bpy.context.view_layer.objects.active = ring
        bpy.ops.wm.stl_export(filepath=combined_path, export_selected_objects=True)
        print(f"  exported -> {combined_path}  (import THIS one)")

    if RENDER_IMAGES:
        apply_color(ring, "ring_color", ELEMENT_COLORS["ring"])
        apply_color(white, "white_color", ELEMENT_COLORS["hub"])
        for key, obj in inserts.items():
            apply_color(obj, f"{key}_color", ELEMENT_COLORS[key])
        center, size = compute_scene_bounds()
        render_angles(center, size, os.path.join(out_dir, "renders"))

    return ring

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) not in (2, 3):
        raise SystemExit('Usage: blender --background --python gear_name_tag.py -- "First" "Last" ["Phone"]')
    build(argv[0], argv[1], phone=argv[2] if len(argv) == 3 else None)
    print("Import ring.stl + white_cog.stl + logo.stl + molndal.stl + firstname.stl + surname.stl")
    print("(+ phone.stl if a phone number was given) together; they share coordinates")
    print("and align automatically. Assign a filament/color to each (molndal+firstname")
    print("+surname+phone share black — 4 colors total).")
    print("Done.")
