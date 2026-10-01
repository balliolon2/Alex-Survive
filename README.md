# Alex-Survive 🌲⛏️

A 3D Survival Game built with **Godot Engine 4.7** and **Blender**, with full **MCP (Model Context Protocol)** support for AI-assisted development.

---

## 📁 Project Structure

```text
Alex-Survive/
├── blender/                          # 🎨 Source 3D Assets (Raw .blend files, high-poly sculpts)
│   ├── characters/                   # Character models, armatures, rigs
│   ├── environment/                  # World meshes, terrain, foliage, buildings
│   ├── items/                        # Collectibles, craftables, food, tools
│   ├── weapons/                      # Melee weapons, bows, tools
│   └── textures_src/                 # Raw textures, concept art, bakes
│
├── alex-survive-godot/               # 🎮 Godot 4.7 Game Project
│   ├── project.godot                 # Godot Engine project settings
│   │
│   ├── assets/                       # Game-ready assets imported into engine
│   │   ├── models/                   # Exported .glb / .gltf files from Blender
│   │   │   ├── characters/
│   │   │   ├── environment/
│   │   │   ├── items/
│   │   │   └── weapons/
│   │   ├── textures/                 # PBR textures (Albedo, ORM, Normal)
│   │   ├── materials/                # Shared StandardMaterial3D / Shaders (.tres)
│   │   ├── audio/                    # Sound effects (.wav) & Music (.ogg)
│   │   │   ├── sfx/
│   │   │   └── music/
│   │   └── ui/                       # UI fonts, icons, HUD sprites, themes
│   │
│   ├── scenes/                       # Godot Scene tree files (.tscn)
│   │   ├── core/                     # Main scene, world loop, game managers
│   │   ├── characters/               # Player, Enemies, NPCs
│   │   ├── environment/              # World chunks, levels, foliage scatter
│   │   ├── items/                    # Spawned / dropped items in the world
│   │   └── ui/                       # Menus, inventory screen, health bars
│   │
│   ├── scripts/                      # GDScript source code (.gd)
│   │   ├── autoload/                 # Global singletons (GameManager, EventBus)
│   │   ├── characters/               # Character controller, physics, AI states
│   │   ├── items/                    # Item logic, consumables, equipment
│   │   ├── systems/                  # Survival mechanics (Hunger, Health, Inventory, Crafting)
│   │   └── ui/                       # UI view controllers
│   │
│   └── resources/                    # Custom Godot Resource definitions (.tres)
│       ├── items/                    # Item definition resources (ItemData.tres)
│       └── stats/                    # Entity stats definitions
│
├── docs/                             # Project documentation & design specs
└── .gitignore                        # Root gitignore (excludes caches & .blend backups)
```

---

## 🔄 Asset Pipeline: Blender ➔ Godot

1. **Source in Blender (`blender/`)**:
   - Work on 3D models in their respective folder under `blender/` (e.g. `blender/characters/alex.blend`).
   - Use Metric units (Length: Meters, Unit Scale: 1.0) with Forward: `-Y` and Up: `+Z`.

2. **Export to Godot (`alex-survive-godot/assets/models/`)**:
   - Export game-ready models as **`.glb`** (Binary glTF) directly into `alex-survive-godot/assets/models/<category>/`.
   - Godot 4 automatically imports `.glb` and creates inherited scenes or meshes.

3. **In-Engine Assembly (`alex-survive-godot/scenes/`)**:
   - Create a new Scene (e.g. `scenes/characters/player.tscn`) using `CharacterBody3D`.
   - Instance the `.glb` model, add collision shapes (`CollisionShape3D`), and attach the controller script (`scripts/characters/player.gd`).

---

## 🤖 MCP AI Control

* **Blender MCP (`mcp-for-blender`)**: Controls Blender via Python `bpy` (generate geometry, apply materials, export glTF/GLB).
* **Godot MCP (`@coding-solo/godot-mcp`)**: Controls Godot (launch editor, run project, create scenes, add nodes, inspect debug logs).