# Developer Notes: Alex-Survive 📝

Notes on the user's setup, toolchain, MCP integrations, and technical pipeline.

---

## 1. Toolchain & Environment

- **Host OS**: Windows (Powershell)
- **Engine**: Godot Engine 4.7 (`alex-survive-godot/project.godot`)
  - Rendering Engine: `Forward+` (D3D12 driver on Windows)
  - Physics Engine: `Jolt Physics`
  - Display: `canvas_items` stretch mode, expand aspect ratio
- **DCC 3D Modeling**: Blender 4.x (`blender/`)
- **MCP Servers Connected**:
  - `mcp-for-blender`: Controls Blender via `bpy` execution, polyhaven asset downloads, glTF/GLB export.
  - `@coding-solo/godot-mcp`: Launches Godot editor, runs game project, captures debug logs, creates scenes, adds nodes.

---

## 2. Technical Pipeline: Blender ➔ Godot

### Step 1: Modeling & Rigging in Blender
- Units: Metric, Unit Scale: 1.0
- Orientation: Forward = `-Y`, Up = `+Z`
- Target Polycount: Stylized Mid-Poly (optimized for crisp comic contours)
- Texture Format: ORM Packed PBR (Red = Occlusion, Green = Roughness, Blue = Metallic) + Albedo + Normal Map
- Location: `blender/<category>/<asset_name>.blend`

### Step 2: Automated glTF / GLB Export via MCP
- Export target: `alex-survive-godot/assets/models/<category>/<asset_name>.glb`
- Godot 4 automatically imports `.glb` and provides scene generation.

### Step 3: Comic Post-Processing Shader in Godot
- Post-process quad / `CompositorEffect` or Fullscreen Quad with Custom Shader:
  - Sobel Edge detection on Depth & Normal buffers for ink outlines.
  - Step function / banded diffuse lighting for graphic novel contrast.

---

## 3. Session & Progression Architecture

- **Cycle Ladder**:
  - Day 1–2: Walkers (Tuning: 15–20 zombies per night).
  - Day 3–4: Walkers + Runners (Tuning: 25–35 zombies, 20% runners).
  - Day 5–6: Walkers + Runners + Brute (Tuning: 40+ zombies, 1–2 Brutes).
  - Day 7–8: Walkers + Runners + Brutes + Tank (Boss wave).
  - Day 9+: Cyclical infinite scaling (+15% HP & damage, increased pack sizes).
- **Core Loop**:
  - Day Phase: Scavenge ruined building, fortify barricades, hunt/fish outdoors, repair gear.
  - Night Phase: Survive wave, protect chokepoints, fall back floor-by-floor.
  - Permadeath: Tally days, kills, score.
