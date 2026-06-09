# Buckle Part 2 v1
# Frame:  20×45mm round bar, NO centre bar
# Mount:  D-shaped, same as part 1
# Dome:   50mm Ø, no torus, centre hole for part 1 disc
# Part 2 is rotated 180° so it mirrors part 1 when assembled.
# Part 1 shown at x=-120 for reference.
#
# Paste into Blender Script Editor and run (Alt+P).

import bpy, bmesh, math, os
import mathutils

# ── CONFIG ──────────────────────────────────────────────────────
FRAME_W =  20.0
FRAME_H =  45.0
BAR_R   =   2.0

MOUNT_R    = 15.0
MOUNT_T    =  2.0
SURROUND_R =  1.5

ARM_L         = 14.0
ARM_Z_RISE    =  8.0
ARM_H         =  7.0
ARM_THICK_MID =  3.0
ARM_THICK_END =  0.4
ARM_OVERLAP   =  5.0

# Part 1 disc
DISC_D  =  30.0
DOME_H  =   4.5
RING_R  =   1.8

# Part 2 dome
DOME2_D  =  50.0
DOME2_H  =   5.0
HOLE_D   =  36.0   # covers part 1 disc (30mm) + torus ring (1.8mm each side) + clearance

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

def make_cut_box(x_right, r):
    big = (r + 10) * 3
    bpy.ops.mesh.primitive_cube_add(size=big, location=(x_right - big / 2, 0, 0))
    return bpy.context.active_object

# ── SHARED: MOUNT + ARM ─────────────────────────────────────────
def mount_plate(x_flat, name="mount"):
    r, sr = MOUNT_R, SURROUND_R
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG * 2, radius=r, depth=MOUNT_T, location=(x_flat, 0, 0))
    body = bpy.context.active_object
    bool_op(body, make_cut_box(x_flat, r))
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=sr,
        major_segments=SEG * 2, minor_segments=SEG // 2,
        location=(x_flat, 0, 0))
    ring = bpy.context.active_object
    bool_op(ring, make_cut_box(x_flat, r + sr))
    obj = join_all([body, ring])
    obj.name = name
    return obj

def curved_arm(x0, z0, x1, z1, arm_h, thick_mid, thick_end, n=16, name="arm"):
    dx  = x1 - x0
    cp1 = (x0 + dx * 0.30, z0)
    cp2 = (x0 + dx * 0.70, z1)
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
        t = i / n
        bx, bz = bez(t)
        tx, tz = bez(min(t + 0.001, 1.0))
        nx = -(tz - bz);  nz = (tx - bx)
        nl = math.sqrt(nx*nx + nz*nz) or 1e-9
        nx, nz = nx/nl, nz/nl
        tk = thick_end + (thick_mid - thick_end) * math.sin(t * math.pi)
        ht, hh = tk / 2, arm_h / 2
        rings.append([
            bm.verts.new((bx-nx*ht, -hh, bz-nz*ht)),
            bm.verts.new((bx-nx*ht,  hh, bz-nz*ht)),
            bm.verts.new((bx+nx*ht,  hh, bz+nz*ht)),
            bm.verts.new((bx+nx*ht, -hh, bz+nz*ht)),
        ])
    for i in range(len(rings)-1):
        a, b = rings[i], rings[i+1]
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

def build_frame(centre_bar=True):
    hw = FRAME_W / 2
    hh = FRAME_H / 2
    r  = BAR_R
    parts = []
    corners = [(-hw,-hh,0),(hw,-hh,0),(hw,hh,0),(-hw,hh,0)]
    for i in range(4):
        parts.append(bar_seg(corners[i], corners[(i+1)%4], r, f"side{i}"))
    for i, c in enumerate(corners):
        parts.append(knuckle(c, r, f"corner{i}"))
    if centre_bar:
        parts.append(bar_seg((0,-hh,0), (0,hh,0), r, "midbar"))
        parts.append(knuckle((0,-hh,0), r, "mk_b"))
        parts.append(knuckle((0, hh,0), r, "mk_t"))
    return parts

# ── PART 1 DISC ─────────────────────────────────────────────────
def dome_disc(cx, cy, cz, r, dome_h, ring_r):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=r, location=(cx, cy, cz), segments=SEG*2, ring_count=SEG)
    dome = bpy.context.active_object
    dome.scale.z = dome_h / r
    bpy.ops.object.transform_apply(scale=True)
    cut_h = dome_h + 2.0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz - cut_h/2))
    c = bpy.context.active_object
    c.dimensions = (r*2+4, r*2+4, cut_h)
    bpy.ops.object.transform_apply(scale=True)
    bool_op(dome, c)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r+ring_r, minor_radius=ring_r,
        major_segments=SEG*2, minor_segments=SEG//2,
        location=(cx, cy, cz))
    ring = bpy.context.active_object
    obj = join_all([dome, ring])
    obj.name = "dome_p1"
    return obj

# ── PART 2 DOME WITH HOLE ────────────────────────────────────────
def dome_with_hole(cx, cy, cz, outer_r, dome_h, hole_r):
    """Spherical cap dome, no torus. Centre hole for part 1 disc to slot through."""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=outer_r, location=(cx, cy, cz), segments=SEG*2, ring_count=SEG)
    dome = bpy.context.active_object
    dome.scale.z = dome_h / outer_r
    bpy.ops.object.transform_apply(scale=True)
    # cut bottom hemisphere
    cut_h = dome_h + 2.0
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz - cut_h/2))
    bot = bpy.context.active_object
    bot.dimensions = (outer_r*2+4, outer_r*2+4, cut_h)
    bpy.ops.object.transform_apply(scale=True)
    bool_op(dome, bot)
    # centre hole — centered at mid-dome height, generously deep
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=SEG*2, radius=hole_r,
        depth=dome_h * 3,
        location=(cx, cy, cz + dome_h / 2))
    hole = bpy.context.active_object
    bool_op(dome, hole)
    dome.name = "dome_p2"
    return dome

# ── BUILD PART 1 (reference, parked left) ───────────────────────
def build_part1():
    hw    = FRAME_W / 2
    parts = build_frame(centre_bar=True)
    parts.append(mount_plate(hw, "p1_mount"))
    arm_x0  = hw + MOUNT_R
    arm_x1  = arm_x0 + ARM_L
    disc_cx = arm_x1 - ARM_OVERLAP + DISC_D / 2
    arm_obj  = curved_arm(arm_x0, 0, arm_x1, ARM_Z_RISE,
                           ARM_H, ARM_THICK_MID, ARM_THICK_END, name="p1_arm")
    dome_obj = dome_disc(disc_cx, 0, ARM_Z_RISE, DISC_D/2, DOME_H, RING_R)
    bool_op(dome_obj, arm_obj, 'UNION')
    obj = join_all(parts + [dome_obj])
    obj.name = "buckle_part1_ref"
    obj.location.x = -120
    obj.location.y =  120
    return obj

# ── BUILD PART 2 ─────────────────────────────────────────────────
def build_part2():
    hw    = FRAME_W / 2
    parts = build_frame(centre_bar=False)
    parts.append(mount_plate(hw, "p2_mount"))

    # Dome sits directly past the D-mount curved edge, no arm
    disc_cx = hw + MOUNT_R + DOME2_D / 2

    dome_obj = dome_with_hole(disc_cx, 0, 0, DOME2_D/2, DOME2_H, HOLE_D/2)

    obj = join_all(parts + [dome_obj])
    obj.name = "buckle_part2_v1"
    obj.rotation_euler.z = math.pi
    bpy.ops.object.transform_apply(rotation=True)
    return obj

# ── MAIN ────────────────────────────────────────────────────────
clear_scene()

print("Building part 1 (reference)…")
build_part1()

print("Building part 2…")
part2 = build_part2()

if EXPORT_STL:
    export_stl(part2, "buckle_part2_v1")

print("Done.")
