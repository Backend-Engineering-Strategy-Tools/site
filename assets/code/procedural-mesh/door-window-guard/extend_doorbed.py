"""
Extend the door-bed body's KARM opening along its length axis (Blender bpy,
headless-verifiable). NOT a from-scratch part, this edits the found STL in
place.

The block at the far end (x~166-181) isn't one uniform piece - it's two
things stacked in Y: a plain continuation of the main body's own
tapered/slotted profile (Y>=145.77, the shaft's own constant edge value)
sitting on top of a separate flange/pedestal (Y<145.77) that's the actual
bolt-hole housing for obj_2_newhead's pivot. Confirmed by bisecting: two
distinct, non-overlapping internal loops - the main slot continuing
through (upper) and the round bolt hole (lower), split cleanly by Y=145.77.

v6 split along Y correctly (leg = the flange only, kept the upper
continuation attached to the main body) but still cut the *body* side at
X=166 - right where the main slot is still present, so the extension there
still needed a hollow (outer-minus-slot) box. Small residual non-manifold
edges at that seam.

v7 (this version): the main slot doesn't run the whole way to the tip -
bisecting in 0.1mm steps found it closes off completely between x=173.9
and x=174.0. From there to the tip (181.39) the upper continuation (once
the flange is removed) is completely solid - no slot, no bolt hole,
nothing. So: keep the *leg* extraction at its own natural boundary
(LEG_CUT_X=166, where the flange begins - unrelated to where the slot
closes), but do the body-side cut/extension further out, at
BODY_CUT_X=177 (comfortably past the 174 closure point, before the 181.39
tip) - a genuinely clean, solid, feature-free cross-section. The extension
there can be a plain SOLID box - no hole to account for at all - simpler
and more robust than v6's hollow box, since there's nothing left to get
subtly wrong.

  1. "leg" = the bolt-hole flange only: X>=LEG_CUT_X (166) AND Y<CUT_Y
     (145.77) - its own natural boundary, cut off as one piece via
     box-intersect. RIGIDLY TRANSLATED by +EXTENSION.
  2. "shaft_side" = X<=BODY_CUT_X (177) MINUS the leg's box (removes any
     flange portion that would otherwise still be attached in the
     166-177 span) - kept in place, untranslated.
  3. "tip_side" = X>=BODY_CUT_X (177) MINUS the leg's box - this range is
     already past where the flange and the slot both end, so this is
     just the plain solid tip. RIGIDLY TRANSLATED by +EXTENSION.
  4. "extension" = plain SOLID box (outer envelope only, measured at
     BODY_CUT_X, Y from CUT_Y up to the outer edge - no internal void to
     subtract) bridging shaft_side's new exposed end to tip_side's new
     position.
  5. Union shaft_side + extension + tip_side + leg.

Run: blender --background --python extend_doorbed.py
"""

import bpy
import bmesh
import mathutils

SRC = "/Users/mannil/best/site/input/garage/door-window-guard/doorholderv1bam_stls/obj_1_doorbed14deg.stl"
OUT = "/Users/mannil/best/site/assets/code/procedural-mesh/door-window-guard/obj_1_doorbed14deg_extended.stl"

AXIS = 0           # X
EXTENSION = 40.0   # mm added to the KARM opening (82mm -> 122mm)
LEG_CUT_X = 166.0  # natural flange/shaft boundary - unrelated to the slot's own extent
BODY_CUT_X = 177.0  # past where the main slot closes (~174), clean solid zone
CUT_Y = 145.77      # main body's own constant edge - separates the bolt-hole
                     # flange (below) from the plain taper+slot continuation (above)
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


def main():
    clear_scene()

    probe = import_copy(SRC)
    bx, by, bz = world_bounds(probe)
    bounds3 = ((bx[0] - MARGIN, bx[1] + MARGIN),
               (by[0] - MARGIN, by[1] + MARGIN),
               (bz[0] - MARGIN, bz[1] + MARGIN))
    bpy.data.objects.remove(probe, do_unlink=True)

    # the bolt-hole flange's own box: X>=LEG_CUT_X, Y<CUT_Y, full Z margin -
    # its own natural boundary, independent of BODY_CUT_X. (Tried a small
    # deliberate Y-overlap between the INTERSECT/DIFFERENCE versions of this
    # box, matching the fix that helped an X-seam earlier in this project -
    # it made this particular seam worse, 25->40 non-manifold edges. No
    # universal rule here; exact-touch is what's kept for this one.)
    leg_box_verts, leg_box_faces = box_verts_faces(
        LEG_CUT_X, bounds3[0][1], bounds3[1][0], CUT_Y, bounds3[2][0], bounds3[2][1]
    )

    leg = import_copy(SRC)
    leg_cutter = make_object("leg_box_a", leg_box_verts, leg_box_faces)
    apply_boolean(leg, leg_cutter, 'INTERSECT')
    off = [0.0, 0.0, 0.0]
    off[AXIS] = EXTENSION
    translate_apply(leg, off)

    shaft_side = import_copy(SRC)
    apply_boolean(shaft_side, make_box(bounds3[AXIS][0] - 10, BODY_CUT_X, AXIS, bounds3, "box_shaft"), 'INTERSECT')
    leg_cutter_shaft = make_object("leg_box_shaft", leg_box_verts, leg_box_faces)
    apply_boolean(shaft_side, leg_cutter_shaft, 'DIFFERENCE')

    tip_side = import_copy(SRC)
    apply_boolean(tip_side, make_box(BODY_CUT_X, bounds3[AXIS][1] + 10, AXIS, bounds3, "box_tip"), 'INTERSECT')
    leg_cutter_tip = make_object("leg_box_tip", leg_box_verts, leg_box_faces)
    apply_boolean(tip_side, leg_cutter_tip, 'DIFFERENCE')
    translate_apply(tip_side, off)

    loops = cross_section_loops(SRC, BODY_CUT_X)
    outer = loops[-1]
    n_internal = len(loops) - 1
    print(f"at BODY_CUT_X={BODY_CUT_X}: outer Y=[{outer[1]:.2f},{outer[2]:.2f}] Z=[{outer[3]:.2f},{outer[4]:.2f}]  "
          f"internal loops present: {n_internal} (expect 0 - past slot closure, past flange)")

    ext_lo = BODY_CUT_X - OVERLAP
    ext_hi = BODY_CUT_X + EXTENSION + OVERLAP
    outer_verts, outer_faces = box_verts_faces(ext_lo, ext_hi, CUT_Y, outer[2], outer[3], outer[4])
    extension = make_object("extension", outer_verts, outer_faces)

    apply_boolean(shaft_side, extension, 'UNION')
    apply_boolean(shaft_side, tip_side, 'UNION')
    apply_boolean(shaft_side, leg, 'UNION')
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


if __name__ == "__main__":
    main()
