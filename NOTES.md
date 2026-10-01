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

### Step 3: Comic Post-Processing Component in Godot
- **Component Scene**: `alex-survive-godot/scenes/environment/comic_post_process.tscn`
- **Controller Script**: `alex-survive-godot/scripts/systems/comic_post_process.gd`
- **Shader Resource**: `alex-survive-godot/assets/shaders/comic_post_process.tres`
- **How to use**:
  - Drag and drop `comic_post_process.tscn` as a child node of any 3D level scene or player camera.
  - Automatically outlines any imported 3D mesh (characters, buildings, barricades, zombies).
- **Key Inspector Parameters**:
  - `outline_thickness` (default: 1.2): Width of ink outlines in pixels.
  - `depth_threshold` (default: 0.035): Distance silhouette sensitivity.
  - `normal_threshold` (default: 0.45): Surface crease and corner sensitivity.
  - `enable_tone_stepping` (default: true): Quantizes lighting into comic book bands.
  - `shadow_bands` (default: 4): Number of distinct lighting bands.
  - `enable_halftone` (default: true): Authentic 45-degree Ben-Day screen tones in deep shadow.
  - `halftone_scale` (default: 3.5): Density and spacing of halftone dots.

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
