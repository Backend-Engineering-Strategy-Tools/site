# Scarf Slide (woggle) — sibling of the gear name tag, same front medallion
# (cog + fleur-de-lis), different back: instead of text on the medallion
# itself, a half-pipe channel (holds a rolled/folded neckerchief) is fused to
# the medallion's back, and a wider white nameplate (70x40mm) is mounted
# below and behind the channel, with the name recessed into it.
# Genuine multi-material printing (Kobra X / ACE Gen2, Bambu AMS, etc.):
# ring, half_pipe, white_cog, logo, sign, and name are each their own STL,
# sharing one coordinate space so they align automatically on import.
#
# Run headless per name:
#   blender --background --python scarf_slide.py -- "Manfred"

import bpy
import bmesh
import json
import math
import mathutils
import os
import sys
import zipfile

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

# BACK: no text on the medallion itself anymore. Instead, a half-pipe
# channel is fused to the medallion's back for a rolled/folded neckerchief
# to sit in — the medallion's own flat back face acts as the channel's lid,
# so the channel cross-section only needs the open "C" (see build_half_pipe).
HALF_PIPE_INNER_R = 14.0   # mm — fits a rolled scarf roughly 28mm across
HALF_PIPE_WALL    = 2.5    # mm — channel wall thickness
HALF_PIPE_OUTER_R = HALF_PIPE_INNER_R + HALF_PIPE_WALL
HALF_PIPE_LENGTH  = 36.0   # mm — along X, a bit less than the medallion's own diameter
HALF_PIPE_SEGMENTS = 24    # arc resolution

# White nameplate — a rectangular plate wider than the medallion itself, NOT
# stacked behind it — coplanar instead: the sign has a medallion-shaped slot
# cut out of its top edge (see the slot cutout in build_sign), and the
# medallion sits in that slot like a puzzle piece. Both then share the same
# front-face convention and can print flat, face-down, in the same
# orientation — stacking them in Z (tried first) made that impossible.
SIGN_WIDTH     = 40.0
SIGN_HEIGHT    = 40.0
SIGN_THICKNESS = THICKNESS   # same thickness as the medallion — coplanar pieces need a flush back, not a step
SIGN_SLOT_CLEARANCE = 0.2   # mm — how much bigger the slot is than the medallion, for a loose insert fit
SIGN_OVERLAP_FRAC = 0.50   # fraction of sign height the medallion overlaps into (i.e. how deep the slot cuts)
# The medallion's own round body (radius OUTER_R=21) reaches further down
# than the half-pipe does, so "below" has to clear the medallion, not just
# the pipe — and now deliberately overlaps it by SIGN_OVERLAP_FRAC.
SIGN_Y_CENTER  = -OUTER_R + SIGN_OVERLAP_FRAC * SIGN_HEIGHT - SIGN_HEIGHT / 2
SIGN_Z_CENTER  = 0.0   # coplanar with the medallion now, no Z offset needed

# TEXT_FONT is a bold condensed face to echo the Mölndals Scoutkår wordmark's
# look (incl. the dotted, blocky Ö) — DIN Condensed Bold is the closest match
# available locally; not the actual brand font.
TEXT_FONT     = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
NAME_SIZE     = 20.0
# The medallion's slot reaches down to the medallion's own bottom tip
# (y = -OUTER_R, ~18mm deep from the sign's top edge) — below that is the
# only band that's solid across the sign's full width. NAME_Y centers the
# name in that band instead of the sign's overall center, clear of the slot.
NAME_Y        = (-OUTER_R + (SIGN_Y_CENTER - SIGN_HEIGHT / 2)) / 2 - SIGN_Y_CENTER
SIGN_MAX_TEXT_WIDTH = 32.0   # mm — auto-shrink if wider than this (SIGN_WIDTH minus margin)

EXPORT_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scarf_slides")
EXPORT_3MF    = True   # combined.3mf — one file, every part pre-colored/pre-split

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
    "ring": COLORS["red"],       # medallion body — full teeth, full side walls
    "half_pipe": COLORS["black"],  # own STL — needs its own filament, not joined into the sign
    "white_cog": COLORS["white"],
    "logo": COLORS["blue"],      # fleur-de-lis
    "sign": COLORS["white"],     # nameplate — same filament slot as white_cog
    "name": COLORS["black"],     # text recessed into the sign — same slot as half_pipe
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

def flip_and_shift_z(obj, shift):
    """Negate Z (scale.z=-1, NOT a 180deg rotation — that would also flip Y)
    then shift up by `shift` — used to bring a face that was built as the
    LOCAL MAXIMUM z (e.g. the medallion's logo face) down to the new z=0,
    with everything else ending up positive above it. That's what makes a
    piece sit flat on the print bed with that face touching down.

    Mirroring via scale pivots around the OBJECT'S OWN origin, not world
    Z=0 — fine for ring/white/logo/half_pipe (built from raw bmesh data
    with vertices already baked in world space, origin left at the default
    (0,0,0)), but the name text (built via text_add(location=(0,y,z)))
    keeps its origin at that build location. Skipping the reset below
    silently mirrored it around its own z instead of world z=0, offsetting
    it by that same amount — sinking it deeper into the sign than
    intended instead of landing flush."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    cursor_loc = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = cursor_loc
    obj.scale.z = -1
    bpy.ops.object.transform_apply(scale=True)
    obj.location.z = shift
    bpy.ops.object.transform_apply(location=True)

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

def _measure_bevel_surface_radii():
    """The ring's bevel rounds its tooth edges, which shrinks its ACTUAL
    outer/inner radius right at the surface (z = +-THICKNESS/2 — exactly
    where it meets the sign) below the nominal OUTER_R/INNER_R used to
    build it (measured: ~20.72mm and ~17.78mm against a nominal 21/18 —
    the bevel eats ~0.2-0.3mm, more than the slot's own clearance). Sizing
    the sign's slot cutter off the nominal radii left a visible ~0.5mm gap
    around the medallion instead of the intended snug fit. Measuring the
    real, as-built geometry instead of trusting the nominal constants is
    what actually gets this right."""
    temp = _build_gear_solid(OUTER_R, INNER_R, bevel_edges=True)
    mesh = temp.data
    mw = temp.matrix_world
    max_r, min_r = 0.0, float("inf")
    for v in mesh.vertices:
        co = mw @ v.co
        if abs(abs(co.z) - THICKNESS / 2) < 0.01:
            r = math.hypot(co.x, co.y)
            max_r = max(max_r, r)
            min_r = min(min_r, r)
    mesh_data = temp.data
    bpy.data.objects.remove(temp, do_unlink=True)
    bpy.data.meshes.remove(mesh_data)
    return max_r, min_r

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
    inset by TEETH_INLAY_INSET, kept as ONE piece that holds the front logo
    recess — no separate circular hub needed, since the inset cog's own root
    is already big enough for the lily.

    Tradeoff, chosen deliberately over a shallow front-only inlay (tried
    first, on the sibling name-tag project): white_cog's own tooth
    side-walls are exposed at the inset boundary — a shallow (0.6mm) version
    avoided that but was too fragile to print/handle as its own piece."""
    ring = _build_gear_solid(OUTER_R, INNER_R)
    ring.name = "ring"

    white = _build_gear_solid(OUTER_R - TEETH_INLAY_INSET, INNER_R - TEETH_INLAY_INSET,
                               tooth_frac=WHITE_TOOTH_FRAC, bevel_edges=False)
    white.name = "white_cog"

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = white
    white.select_set(True)
    bpy.ops.object.duplicate()
    cutter = bpy.context.active_object
    cutter.name = "white_cog_cutter"
    cutter.scale.z = (THICKNESS + 2) / THICKNESS
    bpy.ops.object.transform_apply(scale=True)

    _boolean_diff(ring, cutter)

    return ring, white

def build_half_pipe():
    """Semi-circular channel (open 'C' cross-section), local frame — flat
    open side at z=0 curving toward +Z, centered at the origin. Fused to the
    SIGN (not the medallion) by the caller, which positions and rotates it
    first. Cross-section is extruded along X."""
    z0 = 0.0
    steps = HALF_PIPE_SEGMENTS
    profile_yz = []
    for i in range(steps + 1):
        theta = math.pi * i / steps
        profile_yz.append((HALF_PIPE_OUTER_R * math.cos(theta), z0 + HALF_PIPE_OUTER_R * math.sin(theta)))
    for i in range(steps, -1, -1):
        theta = math.pi * i / steps
        profile_yz.append((HALF_PIPE_INNER_R * math.cos(theta), z0 + HALF_PIPE_INNER_R * math.sin(theta)))

    bm = bmesh.new()
    x0 = -HALF_PIPE_LENGTH / 2
    verts = [bm.verts.new((x0, y, z)) for y, z in profile_yz]
    face = bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ret = bmesh.ops.extrude_face_region(bm, geom=[face])
    extruded_verts = [v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(HALF_PIPE_LENGTH, 0, 0), verts=extruded_verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("half_pipe")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("half_pipe", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_sign(name):
    """White nameplate — same thickness as the medallion, and the name is
    recessed into its TOP face (+SIGN_THICKNESS/2), the same face convention
    as the medallion's own front (logo). That match matters: sign and
    medallion are coplanar now, viewed from the same direction, so the name
    needs the 'top'-face convention (naturally readable, no mirroring) —
    not the old 'bottom'-face convention the earlier Z-stacked design used,
    which would have read backwards once the two pieces share one front.

    A medallion-shaped slot is cut out of the sign's top edge last (same
    EXACT-solver ordering rule as the name-tag project's keyring hole — cut
    full-depth features after every other boolean on the piece) so the
    medallion inserts into it like a puzzle piece instead of sitting behind
    it."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, SIGN_Y_CENTER, SIGN_Z_CENTER))
    sign = bpy.context.active_object
    sign.name = "sign"
    sign.scale = (SIGN_WIDTH, SIGN_HEIGHT, SIGN_THICKNESS)
    bpy.ops.object.transform_apply(scale=True)

    face_z = SIGN_Z_CENTER + SIGN_THICKNESS / 2   # top face — same convention as the medallion's front

    def make_name(extra_top):
        lo, hi = face_z - INSERT_DEPTH, face_z + extra_top
        center_z = (lo + hi) / 2
        half_thick = (hi - lo) / 2
        bpy.ops.object.text_add(location=(0, SIGN_Y_CENTER + NAME_Y, center_z))
        obj = bpy.context.active_object
        obj.data.body = name.upper()
        obj.data.size = NAME_SIZE
        obj.data.align_x = 'CENTER'
        obj.data.align_y = 'CENTER'
        obj.data.extrude = half_thick
        obj.data.font = bpy.data.fonts.load(TEXT_FONT)
        bpy.ops.object.convert(target='MESH')

        width = obj.dimensions.x
        if width > SIGN_MAX_TEXT_WIDTH:
            scale = SIGN_MAX_TEXT_WIDTH / width
            obj.scale.x = scale
            obj.scale.y = scale
            bpy.ops.object.transform_apply(scale=True)

        # Pre-mirror on X (text is centered on x=0, so this doesn't move it) —
        # the print-flat step (flip_and_shift_z) mirrors the whole sign on Z
        # to keep its X/Y layout untouched, but a mirror is a mirror: it
        # flips chirality, which is invisible on symmetric shapes (gear
        # teeth, the logo) and very visible on text. This X-mirror composes
        # with that later Z-mirror into a proper rotation, so the name reads
        # correctly once the sign sits flat — same fix as the name-tag
        # project's back-face text, same root cause.
        obj.scale.x *= -1
        bpy.ops.object.transform_apply(scale=True)

        recalc_normals(obj)
        force_manifold(obj)
        return obj

    cutter = make_name(extra_top=0.6)
    _boolean_diff(sign, cutter)
    insert = make_name(extra_top=0.0)

    surface_outer_r, surface_inner_r = _measure_bevel_surface_radii()
    slot_cutter = _build_gear_solid(surface_outer_r + SIGN_SLOT_CLEARANCE,
                                     surface_inner_r + SIGN_SLOT_CLEARANCE,
                                     bevel_edges=False)
    slot_cutter.name = "sign_slot_cutter"
    bpy.ops.object.select_all(action='DESELECT')
    slot_cutter.select_set(True)
    bpy.context.view_layer.objects.active = slot_cutter
    slot_cutter.scale.z = (SIGN_THICKNESS + 2) / SIGN_THICKNESS
    bpy.ops.object.transform_apply(scale=True)
    _boolean_diff(sign, slot_cutter)

    return sign, insert

# ----------------------------
# LOGO element
# ----------------------------
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
    LOGO_STAMP's comment) instead of a font glyph. `size` multiplies the
    JSON's already-baked-to-mm coordinates; `y` is a plain Y offset (no
    rotation/mirroring needed — the stamp is only ever used on the front)."""
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

def recess_and_export_logo(plate):
    """Only one recessed element on this piece now (the lily) — no back-face
    text on the medallion at all, so this is much simpler than the sibling
    name-tag project's version."""
    cutter = make_stamp_obj(LOGO_STAMP, LOGO_SIZE, LOGO_Y, INSERT_DEPTH, extra_top=0.6, face='top')
    _boolean_diff(plate, cutter)
    return make_stamp_obj(LOGO_STAMP, LOGO_SIZE, LOGO_Y, INSERT_DEPTH, extra_top=0.0, face='top')

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

def export_3mf(parts, path):
    """A 3MF is just a zip of a few XML parts — no external library needed.
    Writes every part as its own named <object>, tagged with a color via the
    materials-extension <colorgroup> (not plain core-spec <basematerials> —
    tried that first; Anycubic Slicer Next split the parts correctly but
    showed every one as plain black, so whatever it uses to preview color on
    import isn't reading basematerials' displaycolor). `parts` is a list of
    (obj, (r, g, b, a), name) with r/g/b/a in 0..1."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    colors = []
    color_index = {}

    def color_id(rgba):
        key = tuple(round(c, 4) for c in rgba)
        if key not in color_index:
            color_index[key] = len(colors)
            colors.append(key)
        return color_index[key]

    objects_xml = []
    build_items = []
    next_id = 2   # id=1 is reserved for the colorgroup resource

    for obj, rgba, name in parts:
        mesh = obj.data
        mesh.calc_loop_triangles()
        mw = obj.matrix_world

        verts_xml = "".join(
            f'<vertex x="{co.x:.5f}" y="{co.y:.5f}" z="{co.z:.5f}"/>'
            for co in (mw @ v.co for v in mesh.vertices)
        )
        tris_xml = "".join(
            f'<triangle v1="{t.vertices[0]}" v2="{t.vertices[1]}" v3="{t.vertices[2]}"/>'
            for t in mesh.loop_triangles
        )

        obj_id = next_id
        next_id += 1
        objects_xml.append(
            f'<object id="{obj_id}" name="{name}" type="model" pid="1" pindex="{color_id(rgba)}">'
            f'<mesh><vertices>{verts_xml}</vertices>'
            f'<triangles>{tris_xml}</triangles></mesh></object>'
        )
        build_items.append(f'<item objectid="{obj_id}"/>')

    colors_xml = "".join(
        f'<m:color color="#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}{int(a*255):02X}"/>'
        for (r, g, b, a) in colors
    )

    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">'
        f'<resources><m:colorgroup id="1">{colors_xml}</m:colorgroup>'
        f'{"".join(objects_xml)}</resources>'
        f'<build>{"".join(build_items)}</build></model>'
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    )

    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model_xml)
    print(f"  exported -> {path}")

# Fixed slot convention matching how these prints actually get loaded — not
# robust (a slot only "is" this color if that's what's loaded that day), but
# good enough for a private, non-published shortcut. See EXTRUDER_SLOT below.
EXTRUDER_SLOT = {"black": 1, "blue": 2, "red": 3, "white": 4}

def export_project_3mf(parts, path):
    """PRIVATE convenience export, not part of the public downloads — a
    minimal reproduction of Anycubic Slicer Next's own project-3mf flavor
    (Bambu Studio/OrcaSlicer lineage: Metadata/model_settings.config), found
    by inspecting a file re-saved from that slicer. That slicer doesn't read
    any standard 3MF color hint (tried <basematerials> and <colorgroup>,
    both came out flat black) — it only reads its own `extruder` metadata
    per part, referencing whatever filament is currently loaded in that
    numbered slot. `parts` is a list of (obj, name, extruder_slot)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    leaf_objects_xml = []
    components_xml = []
    parts_config_xml = []
    next_id = 1

    for obj, name, slot in parts:
        mesh = obj.data
        mesh.calc_loop_triangles()
        mw = obj.matrix_world

        verts_xml = "".join(
            f'<vertex x="{co.x:.5f}" y="{co.y:.5f}" z="{co.z:.5f}"/>'
            for co in (mw @ v.co for v in mesh.vertices)
        )
        tris_xml = "".join(
            f'<triangle v1="{t.vertices[0]}" v2="{t.vertices[1]}" v3="{t.vertices[2]}"/>'
            for t in mesh.loop_triangles
        )

        leaf_id = next_id
        next_id += 1
        leaf_objects_xml.append(
            f'<object id="{leaf_id}" type="model">'
            f'<mesh><vertices>{verts_xml}</vertices>'
            f'<triangles>{tris_xml}</triangles></mesh></object>'
        )
        components_xml.append(f'<component objectid="{leaf_id}"/>')
        parts_config_xml.append(
            f'<part id="{leaf_id}" subtype="normal_part">'
            f'<metadata key="name" value="{name}.stl"/>'
            f'<metadata key="extruder" value="{slot}"/></part>'
        )

    parent_id = next_id
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        f'<resources>{"".join(leaf_objects_xml)}'
        f'<object id="{parent_id}" type="model">'
        f'<components>{"".join(components_xml)}</components></object>'
        f'</resources>'
        f'<build><item objectid="{parent_id}"/></build></model>'
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>'
    )

    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>'
    )

    model_settings = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<config>'
        f'<object id="{parent_id}">'
        '<metadata key="name" value="plate"/>'
        f'{"".join(parts_config_xml)}'
        '</object></config>'
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("3D/3dmodel.model", model_xml)
        zf.writestr("Metadata/model_settings.config", model_settings)
    print(f"  exported -> {path}  (private, extruder-slot convention — not published)")

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
def build(name):
    clear_scene()
    ring, white = build_ring_and_white()
    logo = recess_and_export_logo(white)
    sign, name_insert = build_sign(name)

    # Half-pipe fuses to the SIGN, not the medallion — keeps the medallion
    # flat (prints logo-down with no protrusions) and lets the sign+pipe
    # piece be oriented independently for its own best print orientation.
    # Rotated 90deg around Z (the only one of the three axes that keeps the
    # tube's length lying flat against the sign's face while standing the
    # arc up vertically — the other two either pointed the opening somewhere
    # impractical or sent the tube diagonally through the plate).
    half_pipe = build_half_pipe()
    half_pipe.rotation_euler = (0, 0, math.radians(90))
    bpy.ops.object.select_all(action='DESELECT')
    half_pipe.select_set(True)
    bpy.context.view_layer.objects.active = half_pipe
    bpy.ops.object.transform_apply(rotation=True)

    # build_half_pipe's local frame curls toward +Z from its flat side — right
    # when the flat side sat on the sign's FRONT face (curls away, into free
    # space in front). Now it's fused to the BACK face instead, so without
    # this flip it would curl the wrong way — back through the sign's own
    # body — instead of away from it.
    half_pipe.scale.z = -1
    bpy.ops.object.transform_apply(scale=True)

    # Centered on the sign (Y) so it doesn't hang off the bottom edge —
    # measured: the pipe is 36mm long, the sign is only 40mm tall, so there's
    # a narrow ~4mm window (y in [-25,-21]) where it fits within the sign at
    # all. That window still overlaps the medallion's slot substantially
    # (the slot reaches down to y=-21, the medallion's own tip) — a real
    # dimension conflict, not resolved by repositioning alone.
    pipe_y = SIGN_Y_CENTER
    pipe_z = SIGN_Z_CENTER - SIGN_THICKNESS / 2   # fused to the BACK face — the front stays flat for the name
    half_pipe.location = (0, pipe_y, pipe_z)
    bpy.context.view_layer.objects.active = half_pipe
    half_pipe.select_set(True)
    bpy.ops.object.transform_apply(location=True)

    # Kept as its own STL, NOT joined into the sign — it needs its own black
    # filament, same as the medallion's ring/logo split. Joining would have
    # merged it into whatever slot the sign uses (white).
    for obj in (ring, white, logo, sign, name_insert, half_pipe):
        flip_and_shift_z(obj, THICKNESS / 2)

    out_dir = os.path.join(EXPORT_DIR, name)
    export_stl(ring, os.path.join(out_dir, "ring.stl"))
    export_stl(white, os.path.join(out_dir, "white_cog.stl"))
    export_stl(logo, os.path.join(out_dir, "logo.stl"))
    export_stl(sign, os.path.join(out_dir, "sign.stl"))
    export_stl(name_insert, os.path.join(out_dir, "name.stl"))
    export_stl(half_pipe, os.path.join(out_dir, "pipe.stl"))

    if EXPORT_3MF:
        export_3mf([
            (ring, ELEMENT_COLORS["ring"], "red_ring"),
            (white, ELEMENT_COLORS["white_cog"], "white_cog"),
            (logo, ELEMENT_COLORS["logo"], "blue_logo"),
            (sign, ELEMENT_COLORS["sign"], "white_sign"),
            (name_insert, ELEMENT_COLORS["name"], "black_name"),
            (half_pipe, ELEMENT_COLORS["half_pipe"], "black_pipe"),
        ], os.path.join(out_dir, "combined.3mf"))

        def _slot(rgba):
            return next(s for n, s in EXTRUDER_SLOT.items() if COLORS[n] == rgba)

        export_project_3mf([
            (ring, "red_ring", _slot(ELEMENT_COLORS["ring"])),
            (white, "white_cog", _slot(ELEMENT_COLORS["white_cog"])),
            (logo, "blue_logo", _slot(ELEMENT_COLORS["logo"])),
            (sign, "white_sign", _slot(ELEMENT_COLORS["sign"])),
            (name_insert, "black_name", _slot(ELEMENT_COLORS["name"])),
            (half_pipe, "black_pipe", _slot(ELEMENT_COLORS["half_pipe"])),
        ], os.path.join(out_dir, "anycubic_print_ready.3mf"))

    if RENDER_IMAGES:
        apply_color(ring, "ring_color", ELEMENT_COLORS["ring"])
        apply_color(white, "white_color", ELEMENT_COLORS["white_cog"])
        apply_color(logo, "logo_color", ELEMENT_COLORS["logo"])
        apply_color(sign, "sign_color", ELEMENT_COLORS["sign"])
        apply_color(name_insert, "name_color", ELEMENT_COLORS["name"])
        apply_color(half_pipe, "half_pipe_color", ELEMENT_COLORS["half_pipe"])
        center, size = compute_scene_bounds()
        render_angles(center, size, os.path.join(out_dir, "renders"))

    return ring

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) != 1:
        raise SystemExit('Usage: blender --background --python scarf_slide.py -- "Name"')
    build(argv[0])
    print("Import ring.stl + white_cog.stl + logo.stl + sign.stl + name.stl + pipe.stl")
    print("together; they share coordinates and align automatically. Assign a")
    print("filament/color to each (ring=red, white_cog/sign=white, logo=blue,")
    print("name/pipe=black).")
    print("Done.")
