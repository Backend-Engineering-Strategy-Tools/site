# Swedish Scout Belt Buckle — "VAR REDO" (Be Ready)
# Two-piece quarter-turn (bayonet) lock construction.
# Front face: decorative plate with fleur-de-lis + VAR REDO ring — CAST THIS ONE.
# Back plate: flat plate + belt bars — print directly, no need to cast.
#
# Overall assembled size: ~50 × 80 mm
# Front face alone:        ~50 × 50 mm circular
#
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, os

# ── CONFIG ──────────────────────────────────────────────────────

# Front face (nearly circular decorative plate)
FD         = 50.0   # face diameter (mm)
F_T        =  4.0   # base plate thickness
F_CORNER_R =  7.0   # outer corner radius

RING_OD    = 42.0   # text ring outer Ø
RING_ID    = 30.0   # text ring inner Ø
RING_RAISE =  2.0   # ring rises above plate by this much

DISC_D     = 24.0   # central medallion Ø
DISC_RAISE =  1.5   # medallion above ring top

RING_TEXT    = "VAR•REDO•"   # Swedish Scout motto — "Be Ready"
TEXT_R       = 16.5           # character-centre arc radius
TEXT_SIZE    =  3.8
TEXT_EXTRUDE =  0.9

# Tries these paths for a font that renders the bullet "•" cleanly
FONT_PATHS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

# "Crossbow arm" wings on left and right of the front plate
WING_L     = 13.0   # wing length (extends beyond disc edge)
WING_H     = 11.0   # wing height
WING_STEP  =  3.5   # depth of inner step cut — creates the notched crossbow profile

# Back plate
BACK_T     =  2.5   # flat back plate thickness
BAR_EXT    = 15.0   # belt bar frame extension beyond disc on each side
BAR_H      =  9.0   # belt bar frame height
BAR_SLOT_W = 10.0   # open slot width inside the bar frame
BAR_SLOT_H =  5.0   # open slot height inside the bar frame

# Quarter-turn bayonet lock
LOCK_R      =  5.5   # lock post radius
LOCK_POST_H =  3.0   # post height above back of front plate
LOCK_TAB_W  =  7.0   # tab width (must clear keyhole slot)
LOCK_TAB_T  =  2.5   # tab thickness

EXPORT_STL = True
EXPORT_DIR = "/Users/mannil/Documents/STL_BUCKLE"
SEG        = 64

# ── UTILS ───────────────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for m in bpy.data.meshes: bpy.data.meshes.remove(m)
    for c in bpy.data.curves: bpy.data.curves.remove(c)

def bool_op(target, tool, op='DIFFERENCE'):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    mod = target.modifiers.new("b", 'BOOLEAN')
    mod.operation, mod.object, mod.solver = op, tool, 'EXACT'
    bpy.context.view_layer.update()
    bpy.ops.object.modifier_apply(modifier="b")
    bpy.data.objects.remove(tool, do_unlink=True)

def join_all(obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    return bpy.context.active_object

def export_stl(obj, fname):
    os.makedirs(bpy.path.abspath(EXPORT_DIR), exist_ok=True)
    path = os.path.join(bpy.path.abspath(EXPORT_DIR), fname + ".stl")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    print(f"  → {path}")

# ── PRIMITIVES ──────────────────────────────────────────────────
def cyl(r, h, loc=(0,0,0), name="c"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG, radius=r, depth=h,
        location=(loc[0], loc[1], loc[2] + h/2))
    o = bpy.context.active_object
    o.name = name
    return o

def box(x, y, z, loc=(0,0,0), rz=0.0, name="b"):
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=(loc[0], loc[1], loc[2] + z/2))
    o = bpy.context.active_object
    o.dimensions = (x, y, z)
    if rz:
        o.rotation_euler.z = math.radians(rz)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    o.name = name
    return o

def rounded_rect(w, h, r, depth, name):
    """Solid rounded-rectangle plate — convex hull of 4 corner cylinders."""
    corners = [(1,1),(-1,1),(-1,-1),(1,-1)]
    cyls = [cyl(r, depth, (s*(w/2-r), t*(h/2-r), 0), f"rr{i}") for i,(s,t) in enumerate(corners)]
    obj = join_all(cyls)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.name = name
    return obj

def annulus(od, id_, h, loc=(0,0,0), name="ann"):
    outer = cyl(od/2, h, loc, "ann_o")
    inner = cyl(id_/2, h + 0.2, (loc[0], loc[1], loc[2] - 0.1), "ann_i")
    bool_op(outer, inner)
    outer.name = name
    return outer

# ── CIRCULAR TEXT ────────────────────────────────────────────────
def load_font():
    for path in FONT_PATHS:
        if os.path.exists(path):
            return bpy.data.fonts.load(path)
    return None

def arc_text(text, radius, z, size, extrude, name):
    font = load_font()
    n    = len(text)
    step = 2 * math.pi / n
    objs = []
    for i, ch in enumerate(text):
        a = math.pi/2 - i * step          # top-start, clockwise
        bpy.ops.object.text_add(location=(radius*math.cos(a), radius*math.sin(a), z))
        t = bpy.context.active_object
        t.data.body, t.data.size, t.data.extrude = ch, size, extrude
        t.data.align_x, t.data.align_y = 'CENTER', 'CENTER'
        if font:
            t.data.font = font
        t.rotation_euler = (0, 0, a - math.pi/2)
        bpy.ops.object.convert(target='MESH')
        objs.append(bpy.context.active_object)
    obj = join_all(objs)
    obj.name = name
    return obj

# ── FLEUR-DE-LIS ─────────────────────────────────────────────────
def fleur_de_lis(base_z, scale=1.0, raise_h=1.2, name="fdl"):
    """
    Heraldic fleur-de-lis: center petal + two side petals + collar + base.
    At scale=1.0 it fits comfortably inside a 24 mm disc.
    Refine in Sculpt Mode for extra crispness after running the script.
    """
    s = scale
    z = base_z
    h = raise_h
    parts = []

    # ── center petal body (tall narrow oval) ──
    bpy.ops.mesh.primitive_cylinder_add(vertices=SEG, radius=2.0*s, depth=h,
        location=(0, 1.5*s, z + h/2))
    cp = bpy.context.active_object
    cp.scale.x = 0.65
    bpy.ops.object.transform_apply(scale=True)
    parts.append(cp)

    # ── two top lobes of center petal ──
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.8*s,
            location=(sx*1.2*s, 5.5*s, z + h*0.45),
            segments=SEG//2, ring_count=SEG//4)
        lobe = bpy.context.active_object
        lobe.scale.z = 0.55
        bpy.ops.object.transform_apply(scale=True)
        parts.append(lobe)

    # ── side petals (mirrored) ──
    for sx in (-1, 1):
        # main body — wide low oval curving outward
        bpy.ops.mesh.primitive_cylinder_add(vertices=SEG, radius=2.8*s, depth=h,
            location=(sx*3.8*s, 2.0*s, z + h/2))
        sp = bpy.context.active_object
        sp.scale = (0.55, 0.75, 1.0)
        sp.rotation_euler.z = math.radians(sx * -18)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        parts.append(sp)

        # rounded tip
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5*s,
            location=(sx*5.8*s, 2.8*s, z + h*0.4),
            segments=SEG//2, ring_count=SEG//4)
        tip = bpy.context.active_object
        tip.scale.z = 0.5
        bpy.ops.object.transform_apply(scale=True)
        parts.append(tip)

    # ── horizontal collar ──
    bpy.ops.mesh.primitive_cylinder_add(vertices=SEG, radius=4.2*s, depth=h,
        location=(0, -0.5*s, z + h/2))
    collar = bpy.context.active_object
    collar.scale.y = 0.3
    bpy.ops.object.transform_apply(scale=True)
    parts.append(collar)

    # ── base stem ──
    bpy.ops.mesh.primitive_cylinder_add(vertices=SEG, radius=1.5*s, depth=h,
        location=(0, -3.2*s, z + h/2))
    base = bpy.context.active_object
    base.scale.x = 1.1
    bpy.ops.object.transform_apply(scale=True)
    parts.append(base)

    obj = join_all(parts)
    obj.name = name
    return obj

# ── BAYONET LOCK POST (sticks out of front piece back face) ──────
def lock_post(z_base, name="lock_post"):
    """Cylinder + rectangular ear. Insert through back-plate keyhole, twist 90°."""
    post = cyl(LOCK_R, LOCK_POST_H, (0, 0, z_base), "lp_cyl")
    tab  = box(LOCK_TAB_W, LOCK_TAB_T, LOCK_POST_H,
               (-LOCK_TAB_W/2, LOCK_R - 0.5, z_base), name="lp_tab")
    bool_op(post, tab, 'UNION')
    post.name = name
    return post

def lock_keyhole(z_base, depth, name="keyhole"):
    """Matching keyhole slot in the back plate — circle + rectangular slot."""
    circle = cyl(LOCK_R + 0.4, depth + 0.2, (0, 0, z_base - 0.1), "kh_cyl")
    slot   = box(LOCK_TAB_W + 0.5, LOCK_TAB_T + 0.5, depth + 0.2,
                 (-(LOCK_TAB_W + 0.5)/2, LOCK_R - 0.3, z_base - 0.1), name="kh_slot")
    bool_op(circle, slot, 'UNION')
    circle.name = name
    return circle

# ── FRONT FACE ───────────────────────────────────────────────────
def build_front():
    r = FD / 2

    # Circular base plate
    plate = cyl(r, F_T, name="front")

    # Raised text ring
    ring_h = F_T + RING_RAISE
    bool_op(plate, annulus(RING_OD, RING_ID, ring_h, name="ring"), 'UNION')

    # Central medallion disc
    disc_h = F_T + RING_RAISE + DISC_RAISE
    bool_op(plate, cyl(DISC_D/2, disc_h, name="disc"), 'UNION')

    # "VAR REDO" circular text on ring top
    txt = arc_text(RING_TEXT, TEXT_R, ring_h, TEXT_SIZE, TEXT_EXTRUDE, "txt")
    bool_op(plate, txt, 'UNION')

    # Fleur-de-lis on medallion
    fdl = fleur_de_lis(disc_h, scale=0.95, raise_h=1.3, name="fdl")
    # Clip FDL to disc footprint so nothing bleeds beyond the disc edge
    clip = cyl(DISC_D/2 - 0.8, 5.0, (0, 0, disc_h - 0.4), "fdl_clip")
    bool_op(fdl, clip, 'INTERSECT')
    bool_op(plate, fdl, 'UNION')

    # "Crossbow arm" wings — stepped rectangular projections left and right
    # The two-step profile mirrors the crossbow-stock silhouette of the original
    for sx in (-1, 1):
        wing_cx = sx * (r + WING_L/2 - 0.5)   # centre of wing in X
        # Outer wing block (full wing height)
        bool_op(plate,
            box(WING_L, WING_H, F_T, (wing_cx - sx*(WING_L/2 - WING_L/2), 0, 0),
                name=f"wing_o{sx}"),
            'UNION')
        # Step cut: removes a rectangle from the inner-edge of the wing
        # leaving the classic notched "bowstring notch" profile
        bool_op(plate,
            box(WING_STEP + 0.2, WING_H - 5.0, F_T + 0.2,
                (wing_cx - sx*(WING_L/2 - WING_STEP/2), 0, -0.1),
                name=f"wing_step{sx}"),
            'DIFFERENCE')

    # Bayonet lock post on the back face (z=0 downward)
    bool_op(plate,
        lock_post(-LOCK_POST_H, name="lpost"),
        'UNION')

    plate.name = "buckle_front"
    return plate

# ── BACK PLATE ───────────────────────────────────────────────────
def build_back():
    r = FD / 2

    # Flat circular plate matching front face footprint
    plate = cyl(r, BACK_T, name="back")

    # Mirror the crossbow wings (so back and front align when assembled)
    for sx in (-1, 1):
        wing_cx = sx * (r + WING_L/2 - 0.5)
        bool_op(plate,
            box(WING_L, WING_H, BACK_T, (wing_cx, 0, 0), name=f"bwing_o{sx}"),
            'UNION')
        bool_op(plate,
            box(WING_STEP + 0.2, WING_H - 5.0, BACK_T + 0.2,
                (wing_cx - sx*(WING_L/2 - WING_STEP/2), 0, -0.1),
                name=f"bwing_step{sx}"),
            'DIFFERENCE')

    # Belt bar frames — extend further left and right beyond the wings
    for sx in (-1, 1):
        bar_cx = sx * (r + WING_L + BAR_EXT/2 - 0.5)
        frame  = box(BAR_EXT, BAR_H, BACK_T, (bar_cx, 0, 0), name=f"bbar{sx}")
        slot   = box(BAR_SLOT_W, BAR_SLOT_H, BACK_T + 0.2,
                     (bar_cx, 0, -0.1), name=f"bslot{sx}")
        bool_op(frame, slot)
        bool_op(plate, frame, 'UNION')

    # Keyhole slot — front piece's lock post inserts and twists 90° to lock
    bool_op(plate, lock_keyhole(0, BACK_T, name="keyhole"), 'DIFFERENCE')

    plate.name = "buckle_back"
    return plate

# ── MAIN ─────────────────────────────────────────────────────────
clear_scene()

print("Building front face…")
front = build_front()

print("Building back plate…")
back = build_back()
back.location.x = FD + 20          # place next to front for easy inspection

if EXPORT_STL:
    print("Exporting…")
    export_stl(front, "buckle_front")
    export_stl(back,  "buckle_back")
    print(f"Written to {EXPORT_DIR}")

print("Done.")
