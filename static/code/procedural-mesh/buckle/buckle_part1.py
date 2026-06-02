# Buckle Part 1 v5
# Frame: 20x45mm round bar, vertical centre bar
# Mount: D-shaped plate (35mm across), torus surround bar, circular slot from curved side
# Arm:   bezier curve in XZ, constant height, thickness tapers thin→thick→thin (sine)
# Disc:  30mm dome + torus ring, boolean union'd with arm (clean junction)
#
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, os
import mathutils

# ── CONFIG ──────────────────────────────────────────────────────
FRAME_W =  20.0
FRAME_H =  45.0
BAR_R   =   2.0   # frame bar radius → 4 mm Ø

# D-shaped mount plate
MOUNT_R      = 15   # radius → 35 mm total Y
MOUNT_T      =  2.0   # plate thickness
SURROUND_R   =  1.5   # surround bar radius → 3 mm Ø

# Bezier arm
ARM_L         = 14.0   # arm length (X)
ARM_Z_RISE    =  8.0   # Z rise from mount to disc
ARM_H         =  7.0   # arm height (Y), constant
ARM_THICK_MID =  3.0   # max thickness at midpoint
ARM_THICK_END =  0.4   # thickness at both ends (tapers to this)
ARM_OVERLAP   =  5.0   # how far arm penetrates dome

# Disc
DISC_D  =  30.0
DOME_H  =   4.5
RING_R  =   1.8   # torus ring bar radius on dome

EXPORT_STL = True
EXPORT_DIR = "/Users/mannil/Documents/STL_BUCKLE"
SEG = 48

# ── UTILS ───────────────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for m in bpy.data.meshes: bpy.data.meshes.remove(m)

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
def cyl(r, h, loc=(0, 0, 0), name="c"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG * 2, radius=r, depth=h,
        location=(loc[0], loc[1], loc[2] + h / 2))
    o = bpy.context.active_object
    o.name = name
    return o

def bar_seg(p1, p2, r, name="seg"):
    v   = mathutils.Vector((p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]))
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG, radius=r, depth=v.length, location=mid)
    o = bpy.context.active_object
    o.rotation_euler = mathutils.Vector((0,0,1)).rotation_difference(v.normalized()).to_euler()
    bpy.ops.object.transform_apply(rotation=True)
    o.name = name
    return o

def knuckle(pos, r, name="k"):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=r, location=pos, segments=SEG, ring_count=SEG // 2)
    o = bpy.context.active_object
    o.name = name
    return o

# ── D-SHAPED MOUNT ───────────────────────────────────────────────
def make_cut_box(x_right, r):
    """Big box whose RIGHT face sits at x_right — cuts everything to the left."""
    big = (r + 10) * 3
    bpy.ops.mesh.primitive_cube_add(size=big, location=(x_right - big / 2, 0, 0))
    o = bpy.context.active_object
    return o

def mount_plate(x_flat, name="mount"):
    """
    D-shaped mount: flat disc body + torus edge ring.
    Each piece is cut separately (clean manifold meshes) then joined.
    """
    r  = MOUNT_R
    sr = SURROUND_R

    # ── flat disc body ──
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG * 2, radius=r, depth=MOUNT_T,
        location=(x_flat, 0, 0))
    body = bpy.context.active_object
    bool_op(body, make_cut_box(x_flat, r))

    # ── torus edge ring — major_radius = r so disc edge sits inside the tube ──
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=sr,
        major_segments=SEG * 2, minor_segments=SEG // 2,
        location=(x_flat, 0, 0))
    ring = bpy.context.active_object
    bool_op(ring, make_cut_box(x_flat, r + sr))

    # Join the two already-clean halves
    obj = join_all([body, ring])
    obj.name = name
    return obj

# ── CURVED ARM ───────────────────────────────────────────────────
def curved_arm(x0, z0, x1, z1, arm_h, thick_mid, thick_end, n=16, name="arm"):
    """
    Arm following a cubic bezier curve in XZ.
    Height (Y) is constant = arm_h.
    Thickness follows a sine profile: thin at both ends, thick in the middle.
    """
    dx  = x1 - x0
    cp1 = (x0 + dx * 0.30, z0)   # leave mount going flat
    cp2 = (x0 + dx * 0.70, z1)   # arrive at disc from below

    def bez(t):
        mt = 1 - t
        bx = mt**3*x0 + 3*mt**2*t*cp1[0] + 3*mt*t**2*cp2[0] + t**3*x1
        bz = mt**3*z0 + 3*mt**2*t*cp1[1] + 3*mt*t**2*cp2[1] + t**3*z1
        return bx, bz

    mesh = bpy.data.meshes.new(name)
    obj  = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm   = bmesh.new()

    rings = []
    for i in range(n + 1):
        t      = i / n
        bx, bz = bez(t)
        # tangent → perpendicular in XZ for thickness direction
        tx, tz = bez(min(t + 0.001, 1.0))
        nx =  -(tz - bz)
        nz =   (tx - bx)
        nl  = math.sqrt(nx*nx + nz*nz) or 1e-9
        nx, nz = nx/nl, nz/nl
        # sine taper — thin at t=0 and t=1, thick at t=0.5
        tk = thick_end + (thick_mid - thick_end) * math.sin(t * math.pi)
        ht, hh = tk / 2, arm_h / 2
        rings.append([
            bm.verts.new((bx - nx*ht, -hh, bz - nz*ht)),
            bm.verts.new((bx - nx*ht,  hh, bz - nz*ht)),
            bm.verts.new((bx + nx*ht,  hh, bz + nz*ht)),
            bm.verts.new((bx + nx*ht, -hh, bz + nz*ht)),
        ])

    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(4):
            bm.faces.new([a[j], a[(j+1)%4], b[(j+1)%4], b[j]])
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.name = name
    return obj

# ── DOME DISC ────────────────────────────────────────────────────
def dome_disc(cx, cy, cz, r, dome_h, ring_r):
    """Spherical cap dome + torus ring at base. cz = Z of dome base."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=r, location=(cx, cy, cz),
        segments=SEG * 2, ring_count=SEG)
    dome = bpy.context.active_object
    dome.scale.z = dome_h / r
    bpy.ops.object.transform_apply(scale=True)
    # cut bottom hemisphere
    cut_h = dome_h + 2.0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz - cut_h / 2))
    cutter = bpy.context.active_object
    cutter.dimensions = (r*2+4, r*2+4, cut_h)
    bpy.ops.object.transform_apply(scale=True)
    bool_op(dome, cutter)
    # torus ring at dome base
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r + ring_r, minor_radius=ring_r,
        major_segments=SEG * 2, minor_segments=SEG // 2,
        location=(cx, cy, cz))
    ring = bpy.context.active_object
    obj = join_all([dome, ring])
    obj.name = "dome_disc"
    return obj

# ── BUILD ────────────────────────────────────────────────────────
def build():
    hw = FRAME_W / 2
    hh = FRAME_H / 2
    r  = BAR_R
    frame_parts = []

    # Rectangular frame
    corners = [(-hw,-hh,0),(hw,-hh,0),(hw,hh,0),(-hw,hh,0)]
    for i in range(4):
        frame_parts.append(bar_seg(corners[i], corners[(i+1)%4], r, f"side{i}"))
    for i, c in enumerate(corners):
        frame_parts.append(knuckle(c, r, f"corner{i}"))

    # Vertical centre bar
    frame_parts.append(bar_seg((0,-hh,0), (0,hh,0), r, "midbar"))
    frame_parts.append(knuckle((0,-hh,0), r, "mk_b"))
    frame_parts.append(knuckle((0, hh,0), r, "mk_t"))

    # D-shaped mount — flat side flush with frame right edge
    frame_parts.append(mount_plate(hw, "mount"))

    # Arm starts at curved edge of D, rises to disc height
    arm_x0  = hw + MOUNT_R
    arm_x1  = arm_x0 + ARM_L
    disc_cx = arm_x1 - ARM_OVERLAP + DISC_D / 2

    arm_obj  = curved_arm(arm_x0, 0, arm_x1, ARM_Z_RISE,
                           ARM_H, ARM_THICK_MID, ARM_THICK_END, name="arm")
    dome_obj = dome_disc(disc_cx, 0, ARM_Z_RISE, DISC_D / 2, DOME_H, RING_R)

    # Union arm into dome — eliminates junction artefacts
    bool_op(dome_obj, arm_obj, 'UNION')

    obj = join_all(frame_parts + [dome_obj])
    obj.name = "buckle_part1_v5"
    obj.location.x -= 120   # park it to the left so part 2 builds at origin
    return obj

# ── MAIN ────────────────────────────────────────────────────────
clear_scene()
print("Building buckle part 1 v5…")
part = build()
if EXPORT_STL:
    export_stl(part, "buckle_part1_v5")
print("Done.")
