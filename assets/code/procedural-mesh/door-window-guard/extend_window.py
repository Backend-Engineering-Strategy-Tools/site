"""
Extend the window-bud body's reach along its length axis (Blender bpy,
headless-verifiable). NOT a from-scratch part, this edits the found STL in
place.

Much simpler than the door body (extend_doorbed.py, seven attempts to get
right): this part has three genuinely distinct zones along X, cleanly
separated, no stacked/overlapping features to untangle.

  1. x=62.30-77.30: near-end mounting block. Full 50mm width, has the
     wall screw hole. Stays fixed - this is where the part attaches to
     the frame.
  2. x=77.30-106.30: a completely hole-free, constant-cross-section zone
     (narrows to the shaft's 20mm width, no holes at all in this span).
     Confirmed by a 0.2mm-step cross-section scan on both edges of this
     range. This is the safe cut/extend zone.
  3. x=106.30-202.13 (tip): contains a long internal slot with a wavy
     Y/Z profile (spring/latch channel for the bolt-lock) plus a stepped
     notch right at the tip. This whole zone is one piece, not stacked
     with anything else the way the door's far block was - confirmed by
     a color-coded render the user reviewed. It just needs to translate
     outward as a rigid block; nothing internal gets touched or resliced.

Technique: cut once inside the safe zone (CUT_X=92.0, comfortably clear
of the transition slivers at both ends of the safe zone). shaft_side
(<=CUT_X) stays in place. tip_side (>=CUT_X, includes the entire lock
mechanism + tip) is rigidly translated by +EXTENSION. extension is a
plain SOLID box (the safe zone has no internal void to subtract) bridging
the two. No leg/flange separation needed - unlike the door body, there's
nothing stacked to pull apart first.

Run: blender --background --python extend_window.py
"""

import bpy
import bmesh
import mathutils

SRC = "/Users/mannil/best/site/input/garage/door-window-guard/obj_1_window_bud.stl"
OUT = "/Users/mannil/best/site/assets/code/procedural-mesh/door-window-guard/obj_1_window_bud_extended.stl"

AXIS = 0          # X
EXTENSION = 40.0  # mm added to the reach, matching the door body's extension
CUT_X = 92.0      # inside the hole-free safe zone (77.3-106.3), clear of
                  # the transition slivers at both ends
OVERLAP = 2.0
MARGIN = 50.0


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for b in list(bpy.data.meshes):
        bpy.data.meshes.remove(b)


def import_copy(path):
    bpy.ops.wm.stl_import(filepath=path)
    return bpy.context.selected_objects[0]


def world_bounds(obj):
    xs, ys, zs = [], [], []
    for c in obj.bound_box:
        wc = obj.matrix_world @ mathutils.Vector(c)
        xs.append(wc.x); ys.append(wc.y); zs.append(wc.z)
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def apply_boolean(target, cutter, operation):
    mod = target.modifiers.new("Bool", 'BOOLEAN')
    mod.object = cutter
    mod.operation = operation
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def make_box(lo, hi, axis, bounds3, name):
    if lo > hi:
        lo, hi = hi, lo
    size = [b[1] - b[0] for b in bounds3]
    center = [(b[0] + b[1]) / 2 for b in bounds3]
    size[axis] = hi - lo
    center[axis] = (lo + hi) / 2
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(center))
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(size)
    return obj


def translate_apply(obj, offset):
    obj.location = tuple(offset)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True)


def cross_section_loops(path, x):
    """All closed loops in the cross-section at plane x, sorted
    largest-vertex-count first, as (n,y_lo,y_hi,z_lo,z_hi)."""
    o = import_copy(path)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    ret = bmesh.ops.bisect_plane(
        bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
        plane_co=(x, 0, 0), plane_no=(1, 0, 0),
        clear_inner=False, clear_outer=False,
    )
    cut_edges = [e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in cut_edges:
        for v in e.verts:
            parent.setdefault(v.index, v.index)
    for e in cut_edges:
        union(e.verts[0].index, e.verts[1].index)
    groups = {}
    for e in cut_edges:
        for v in e.verts:
            groups.setdefault(find(v.index), []).append(v)

    loops = []
    for verts in groups.values():
        ys = [v.co.y for v in verts]
        zs = [v.co.z for v in verts]
        loops.append((len(verts), min(ys), max(ys), min(zs), max(zs)))
    loops.sort(key=lambda t: -t[0])

    bm.free()
    bpy.data.objects.remove(o, do_unlink=True)
    return loops


def main():
    clear_scene()

    probe = import_copy(SRC)
    bx, by, bz = world_bounds(probe)
    bounds3 = ((bx[0] - MARGIN, bx[1] + MARGIN),
               (by[0] - MARGIN, by[1] + MARGIN),
               (bz[0] - MARGIN, bz[1] + MARGIN))
    bpy.data.objects.remove(probe, do_unlink=True)

    loops = cross_section_loops(SRC, CUT_X)
    assert len(loops) == 1, f"expected a single hole-free loop at CUT_X={CUT_X}, found {len(loops)}"
    outer = loops[0]
    print(f"at CUT_X={CUT_X}: outer Y=[{outer[1]:.2f},{outer[2]:.2f}] Z=[{outer[3]:.2f},{outer[4]:.2f}]  "
          f"loops={len(loops)} (expect 1 - hole-free safe zone)")

    shaft_side = import_copy(SRC)
    apply_boolean(shaft_side, make_box(bounds3[AXIS][0] - 10, CUT_X, AXIS, bounds3, "box_shaft"), 'INTERSECT')

    tip_side = import_copy(SRC)
    apply_boolean(tip_side, make_box(CUT_X, bounds3[AXIS][1] + 10, AXIS, bounds3, "box_tip"), 'INTERSECT')
    off = [0.0, 0.0, 0.0]
    off[AXIS] = EXTENSION
    translate_apply(tip_side, off)

    ext_lo = CUT_X - OVERLAP
    ext_hi = CUT_X + EXTENSION + OVERLAP
    outer_verts, outer_faces = box_verts_faces(ext_lo, ext_hi, outer[1], outer[2], outer[3], outer[4])
    extension = make_object("extension", outer_verts, outer_faces)

    apply_boolean(shaft_side, extension, 'UNION')
    apply_boolean(shaft_side, tip_side, 'UNION')
    result = shaft_side

    bm = bmesh.new()
    bm.from_mesh(result.data)
    bmesh.ops.dissolve_degenerate(bm, dist=0.01, edges=bm.edges)
    bm.to_mesh(result.data)
    result.data.update()
    nm_count = len([e for e in bm.edges if not e.is_manifold])
    bm.free()

    final_bx, _, _ = world_bounds(result)
    print(f"OK -> {OUT}  X range={final_bx} (len {final_bx[1]-final_bx[0]:.2f})  nonmanifold={nm_count}")

    bpy.ops.object.select_all(action='DESELECT')
    result.select_set(True)
    bpy.context.view_layer.objects.active = result
    bpy.ops.wm.stl_export(filepath=OUT, export_selected_objects=True)


def make_object(name, verts, faces):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def box_verts_faces(x_lo, x_hi, y_lo, y_hi, z_lo, z_hi):
    verts = [
        (x_lo, y_lo, z_lo), (x_lo, y_hi, z_lo), (x_lo, y_hi, z_hi), (x_lo, y_lo, z_hi),
        (x_hi, y_lo, z_lo), (x_hi, y_hi, z_lo), (x_hi, y_hi, z_hi), (x_hi, y_lo, z_hi),
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    return verts, faces


if __name__ == "__main__":
    main()
