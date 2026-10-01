# Alex-Survive: Last Stand 🌲🏚️🩸

A 3D Post-Apocalyptic Action Horde Survival game built with **Godot Engine 4.7** and **Blender**, powered by **Model Context Protocol (MCP)** for autonomous AI-assisted development.

Inspired by the weighty, high-tension combat and scavenging of *The Last of Us Part II* combined with an endless, escalating wave-defense permadeath challenge in a stylized **Western Comic / Graphic Novel** aesthetic.

---

## 🎯 Game Overview & Core Pillars

- **Genre**: 3D Post-Apocalyptic Action Wave Survival (Permadeath / High-Score)
- **Camera**: Third-Person (Over-the-shoulder / Follow Cam)
- **Art Style**: Western Comic / Graphic Novel (Bold ink outlines, cel-shading, high-contrast lighting)
- **Core Loop**:
  - **☀️ Daytime (Scavenge & Fortify)**: Scavenge scrap and supplies inside a 2-story ruined building, reinforce windows/doors with wooden planks, cook food, fish at the river, hunt wildlife, and repair/mod weapons at the Workbench.
  - **🌙 Nighttime (Horde Wave Defense)**: Defend breach points against hordes of infected, manage melee weapon durability under pressure, conserve scarce ammunition, and fall back floor-by-floor.
  - **💀 Permadeath**: Survive as many days as possible. Endless cyclical escalation until your last stand.

### 🧟 Enemy Escalation Ladder
1. **Days 1–2**: `Walker` only (Slow, swarmers, attack barricades)
2. **Days 3–4**: `Walker` + `Runner` (Fast sprinters, leaping breaches)
3. **Days 5–6**: `Walker` + `Runner` + `Brute` (Bulky miniboss, crushes barricades)
4. **Days 7–8**: Full Assault with `Tank` (Heavily mutated titan)
5. **Day 9+**: Infinite Cyclical Escalation (Density and stats scale continuously until player death)

---

## 📁 Repository Structure

```text
Alex-Survive/
├── GLOSSARY.md                       # Canonical domain terms & entities
├── NOTES.md                          # Dev notes, MCP configurations & formulas
├── README.md                         # Main project overview & documentation
│
├── docs/
│   ├── GDD.md                        # Complete Game Design Document
│   └── agents/                       # Agent guidelines & issue tracking
│
├── workflows/
│   └── blender-godot-pipeline.md     # Automated Blender -> Godot asset workflow
│
├── blender/                          # 🎨 Source 3D Assets (Raw .blend files)
│   ├── characters/                   # Alex, Walkers, Runners, Brutes, Tanks, Wildlife
│   ├── environment/                  # 2-story outpost modular parts, barricades, foliage
│   ├── items/                        # Cans, scrap metal, duct tape, bandages, fish
│   ├── weapons/                      # Lead pipe, baseball bat, shiv, pistol, shotgun
│   └── textures_src/                 # Hand-drawn comic textures & masks
│
├── alex-survive-godot/               # 🎮 Godot 4.7 Game Project
│   ├── project.godot                 # Godot config (Forward+, Jolt Physics, D3D12)
│   ├── assets/
│   │   ├── models/                   # Exported .glb models from Blender
│   │   ├── shaders/                  # Comic edge outline & cel-shade shaders
│   │   ├── textures/                 # PBR textures
│   │   └── audio/                    # Diegetic SFX & atmospheric audio
│   ├── scenes/
│   │   ├── core/                     # Main scene, DayNightCycle, WaveManager
│   │   ├── characters/               # Player (Alex), Infected scenes
│   │   ├── environment/              # Outpost, Barricades, River, Woods
│   │   ├── items/                    # Collectible pickups & interactables
│   │   └── ui/                       # Vitals HUD, Comic death screen, Inventory
│   ├── scripts/
│   │   ├── autoload/                 # GameManager, EventBus, TimeManager
│   │   ├── characters/               # PlayerController, ZombieAI state machines
│   │   ├── systems/                  # Inventory, Durability, Crafting, Barricading
│   │   └── ui/                       # Comic UI controllers
│   └── resources/                    # Custom ItemData and StatData (.tres)
```

---

## 🔄 Asset & Engine Pipeline

1. **Source in Blender (`blender/`)**:
   - Model, texture, and rig assets in Blender using metric units (`Forward: -Y`, `Up: +Z`).
   - Western Comic styling: Hand-painted hatching and high-contrast material nodes.

2. **Automated Export via Blender MCP**:
   - Export optimized game-ready `.glb` directly to `alex-survive-godot/assets/models/<category>/`.

3. **In-Engine Assembly & Testing via Godot MCP**:
   - Assemble nodes into Godot scenes (`CharacterBody3D`, `StaticBody3D` barricades).
   - Test and inspect runtime debug logs with `@coding-solo/godot-mcp`.

---

## 📚 Documentation Quicklinks

- [Game Design Document (GDD)](file:///c:/Users/bond/Documents/Alex-Survive/docs/GDD.md)
- [Domain Glossary](file:///c:/Users/bond/Documents/Alex-Survive/GLOSSARY.md)
- [Developer Notes](file:///c:/Users/bond/Documents/Alex-Survive/NOTES.md)
- [Blender to Godot Pipeline Spec](file:///c:/Users/bond/Documents/Alex-Survive/workflows/blender-godot-pipeline.md)