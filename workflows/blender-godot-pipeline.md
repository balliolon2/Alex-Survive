# Workflow Spec: Blender to Godot Asset Pipeline

> **ID**: `blender-godot-pipeline`  
> **Status**: Active  
> **Tools**: Blender MCP (`execute_blender_code`, `export_scene`), Godot MCP (`create_scene`, `add_node`, `run_project`, `get_debug_output`)

---

## Purpose
Automate the end-to-end creation, export, importing, and scene wiring of 3D game assets from Blender to Godot 4.7 with zero manual file dragging.

---

## Trigger
- New item, weapon, character, or environment mesh requested.

---

## Steps

### 1. Model & Material Generation (Blender MCP)
- Open or create asset in `blender/<category>/<asset_name>.blend`.
- Ensure origin point (pivot) is grounded at base:
  - Characters / Enemies: Ground plane between feet (Z=0).
  - Weapons / Hand items: Grip point at origin.
  - Barricades / Furniture: Snapped to bottom-center.
- Assign material with Western Comic stylization (Base color, high-contrast roughness, optional baked normal or vertex colors).

### 2. GLB Export
- Trigger export via Blender Python / MCP:
  ```python
  import bpy
  bpy.ops.export_scene.gltf(
      filepath="c:/Users/bond/Documents/Alex-Survive/alex-survive-godot/assets/models/<category>/<asset_name>.glb",
      export_format="GLB",
      use_selection=False,
      export_apply=True
  )
  ```

### 3. Godot Scene Assembly (Godot MCP)
- Create new `.tscn` in `alex-survive-godot/scenes/<category>/<asset_name>.tscn`.
- Add Root Node:
  - Entity: `CharacterBody3D`
  - Prop/Barricade: `StaticBody3D` or `Area3D`
  - Item: `RigidBody3D` or `Area3D`
- Instance child nodes:
  - Add `MeshInstance3D` or instance the `.glb`.
  - Add `CollisionShape3D` (Box, Capsule, or Cylinder).
  - Attach appropriate GDScript from `alex-survive-godot/scripts/`.

### 4. Verification Checkpoint
- Launch and run scene via Godot MCP `run_project`.
- Inspect debug logs via `get_debug_output` to ensure zero compilation or import errors.
