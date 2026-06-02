---
title: "Blender Python — Procedural Mesh for 3D Printing"
description: "Using Blender's bpy API to generate parametric geometry and export STL. The right tool when you have a family of similar parts and want the script to be the source of truth."
date: 2026-06-02
draft: false
tags: ["blender", "python", "3d-printing", "parametric", "stl"]
---

Write a Python script that builds geometry programmatically using Blender's `bpy` API, then export as STL. No manual modelling — the script is the source of truth, re-running it regenerates everything.

This pattern is useful when you have a family of similar parts (different sizes, repeated structures, parametric variations) or when the geometry is defined by rules rather than artistic decisions.

---

## When to use this vs. alternatives

| | Blender Python | OpenSCAD | CadQuery |
|---|---|---|---|
| Booleans, extrude, modifiers | ✓ built-in | ✓ CSG only | limited |
| Sculpt / organic shapes | ✓ | ✗ | ✗ |
| Parametric constraints | manual | manual | ✓ strong |
| Python ecosystem | ✓ full stdlib | ✗ own language | ✓ |
| Interactive viewport preview | ✓ | ✗ | ✗ |
| Export to STL | ✓ one call | ✓ | ✓ |

For repetitive mechanical geometry with booleans (holes, sockets, cutouts), Blender Python is the fastest path if you already know Python. The interactive viewport lets you catch geometry problems before exporting.

---

## Core pattern

Every script follows the same structure:

```python
import bpy, bmesh, math, os

# 1. Create a primitive — it becomes bpy.context.object
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=5, depth=3)
obj = bpy.context.object

# 2. Edit vertices directly via bmesh
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
for v in bm.verts:
    if v.co.z > 0:
        v.co.x *= 0.9   # taper the top
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

# 3. Boolean modifier to cut a hole
bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=3.2)
cutter = bpy.context.object
mod = obj.modifiers.new("Hole", 'BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = obj
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter, do_unlink=True)

# 4. Export
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.wm.stl_export(filepath="/tmp/part.stl", export_selected_objects=True)
```

Build complexity by wrapping each operation in a function, then calling it in a loop over a size or parameter list.

---

## Running the script

1. Open Blender → switch to the **Scripting** workspace
2. Click **New** or **Open** to load your `.py` file
3. Click **Run Script** (▶) or press `Alt + P`

Output and errors appear in the system console (`Window → Toggle System Console` on Windows, or launch Blender from a terminal on macOS/Linux).

---

## Key API surface

### Primitives

```python
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=h)
bpy.ops.mesh.primitive_cube_add(size=s)
bpy.ops.mesh.primitive_plane_add(size=s)
```

All primitives land at the world origin and become `bpy.context.object`.

### Transforms

```python
obj.scale = (sx, sy, sz)
obj.location = (x, y, z)
obj.rotation_euler = (rx, ry, rz)   # radians
bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
```

Apply transforms before any bmesh edits — otherwise vertex coordinates are in local (pre-scale) space, and your edit positions won't match world coordinates.

### bmesh (direct vertex / edge / face editing)

```python
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
for v in bm.verts:
    if v.co.z > 0:
        v.co.x *= 0.9
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Boolean modifiers

```python
mod = target.modifiers.new("Name", 'BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'   # or UNION or INTERSECT
mod.solver = 'EXACT'           # more reliable than FAST for tight geometry
bpy.context.view_layer.objects.active = target
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter, do_unlink=True)
```

Apply and remove the cutter immediately — leaving stale cutter objects causes confusion on subsequent runs.

### Joining objects (single boolean cut for a grid of holes)

Rather than applying one boolean per hole, join all cutters first:

```python
for obj in cyl_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = cyl_objects[0]
bpy.ops.object.join()
cutter = bpy.context.active_object
# now do one boolean cut on the plate
```

One boolean operation is faster and produces cleaner topology than N serial cuts.

### STL export (Blender 4.x / 5.x)

```python
bpy.ops.wm.stl_export(filepath="/abs/path/part.stl", export_selected_objects=True)
```

### Collections (organising multi-part output)

```python
col = bpy.data.collections.new("Round Bases")
bpy.context.scene.collection.children.link(col)
for c in obj.users_collection:
    c.objects.unlink(obj)
col.objects.link(obj)
```

---

## Parametric families

The main loop pattern — build one function that takes dimensions, call it for each size:

```python
SIZES = [10, 15, 20, 25]

for w in SIZES:
    obj = make_clip(width=w)
    obj.name = f"clip_{w}mm"
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.wm.stl_export(
        filepath=f"/output/clip_{w}mm.stl",
        export_selected_objects=True
    )
```

Put all tuneable values at the top of the file in a `# CONFIG` block. This makes the script easy to hand to Claude and say "change the hole diameter to 7mm and add two more rows."

---

## Clearing the scene before a run

Add this at the top when iterating interactively — otherwise re-running doubles the objects:

```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)
```

---

## Viewport layout before export

Spread objects out so you can visually review them before committing to an export:

```python
xoff = 0
for obj, w in zip(objects, widths):
    obj.location.x = xoff
    xoff += w + 5
```

For print batches, sort largest-first and pack into rows within your bed dimensions (shelf bin-packing against `PLATE_W × PLATE_H`).

---

## Working with Claude

The config-block pattern pairs well with LLM iteration. Because all tuneable values sit in one place and each operation is a named function, you can describe changes in plain language:

- *"Change `HOLE_DIAM` to 6 and add a third text line below line 2"* — Claude edits two constants and adds a `make_line()` call.
- *"The holes in rows 2 and 3 need 3mm more clearance from the edge"* — Claude adjusts `x_origin` offset computation.
- *"Add a chamfer around the perimeter of the top face"* — Claude adds a bmesh loop and inset operation.

The workflow is: run → look at viewport → describe the problem → apply updated script → repeat. Iteration is fast because the viewport gives immediate visual feedback and the script regenerates from scratch each run.

---

## Limitations

**Booleans are fragile on non-manifold geometry.** If a cutter face is coplanar with the target, or vertices are nearly coincident, Blender's solver can produce garbage. Add a small bleed (0.5–1 mm) so cutters fully penetrate surfaces.

**No parametric constraints.** Unlike CadQuery, there is no "keep this face parallel to that face" system. Dimension changes cascade manually. This is manageable when the config block is the only place numbers live.

**Script state accumulates.** Re-running in an existing scene doubles the objects. Clear the scene first (see above) or check for existing objects by name before creating.

---

## Related

- [Garage — Scripted Parts](/garage/) — hole box and other physical builds using this approach
