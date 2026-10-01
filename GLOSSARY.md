# Domain Glossary: Alex-Survive 📖

Canonical terminology for entities, systems, items, and state models in the Alex-Survive project. All code, scenes, resources, and tests should strictly use these terms.

---

## 1. Entities & Characters

- **Alex (`Player`)**: The playable survivor character. Uses `CharacterBody3D` with third-person locomotion, stamina management, and inventory.
- **`PlayerState`**: Discrete locomotion state machine enum (`IDLE`, `WALK`, `SPRINT`, `CROUCH`, `DODGE`, `DEAD`) preventing conflicting actions and governing locomotion physics.
- **`DodgeAction`**: Grounded, directional evasion step with brief invulnerability window (i-frames) and stamina cost, replacing standard platformer jump.
- **`CameraRig`**: SpringArm3D-based over-the-shoulder follow rig with pitch/yaw collision protection.
- **Infected (`Enemy`)**: The overarching term for all undead enemies. Sub-types:
  - **`Walker`**: Standard slow-moving infected that shuffles toward targets and claws at barricades.
  - **`Runner`**: High-speed, agile infected that sprints, leaps, and flanks.
  - **`Brute`**: Bulky, muscular infected miniboss that breaks barricades with heavy blows.
  - **`Tank`**: Heavily mutated, colossal infected boss with immense health and ground-smash attacks.
- **Wildlife (`Fauna`)**: Non-hostile or skittish animals roaming the outer perimeter (`Rabbit`, `Deer`).
- **Fish (`FishSpot`)**: Interactable fishing point along the creek/river.

---

## 2. Survival Systems & Vitals

- **`VitalsComponent`**: Dedicated modular component node managing health, stamina, and hunger with decoupled event signals.
- **Health (`hp`)**: Hit points of player or entities (0–100). Dropping to zero triggers entity death or game over.
- **Stamina (`stamina`)**: Energy pool (0–100) depleted by sprint, dodge, and melee attacks; regenerates when idle or walking.
- **Hunger (`hunger`)**: Metabolic stat (0–100) depleted over time; thresholds affect stamina recovery rate and damage output.
- **Durability (`durability`)**: Health of a weapon or tool. Decreases per hit; breaks at zero unless repaired at a Workbench.
- **Barricade (`WindowBarricade`, `DoorReinforcement`)**: Contextual fortifiable structure placed over building breach points.
- **Workbench (`Workbench`)**: In-world station used for repairing damaged weapons and applying weapon reinforcements/mods.
- **Campfire (`CookingStation`)**: Heat source used to cook raw meat and raw fish into edible rations.

---

## 3. Items & Resources

- **`ScrapMetal`**: Primary crafting and repair resource collected from ruined shelves, cars, and electronics.
- **`WoodPlank`**: Primary barricading material for windows and doors.
- **`DuctTape`**: Binding agent required alongside Scrap Metal for workbench repairs and reinforces.
- **`Cloth`**: Fabric gathered from upholstery or clothing, used for bandages and molotov wicks.
- **`Alcohol`**: Medical antiseptic and flammable liquid used for bandages and molotovs.
- **`LooseAmmo`**: Ammunition cartridges for firearms (e.g., `PistolAmmo`, `ShotgunShells`).
- **`CannedRation`**: Finite, pre-packaged non-perishable food found in building cabinets.
- **`RawMeat` / `CookedMeat`**: Food gathered from hunting wildlife.
- **`RawFish` / `CookedFish`**: Food gathered from river fishing.

---

## 4. Game Cycle & State

- **`DayNightCycle`**: Singleton or manager controlling world time, light angle, and phase transitions.
- **`DayPhase`**: Safe/preparation phase (06:00 - 18:00) with sunlight, scavenging, and wildlife.
- **`NightPhase`**: Wave defense phase (18:00 - 06:00) with darkness, siren, and horde spawns.
- **`HordeWave`**: Active group of infected spawned during the night, escalating in composition and density.
- **`Permadeath`**: Single-life game session loop that ends in a statistics summary upon player death.

---

## 5. Rendering & Visual Pipeline

- **`ComicShader` (`PostProcessOutline`)**: Screen-space spatial shader applied over the 3D viewport to generate graphic novel ink outlines and tone separation.
- **`SobelFilter` (`EdgeDetection`)**: Convolution kernel algorithm sampling depth and normal texture buffers to locate geometry silhouettes and surface creases.
- **`DepthThreshold` / `NormalThreshold`**: Configurable tolerance parameters to prevent flat surfaces (floors/terrain) from rendering unwanted outline noise while keeping sharp edges crisp.
- **`HalftoneShading` (`ScreenTone`)**: Dot matrix or crosshatch pattern applied strictly to shaded/shadowed pixel areas to simulate printed comic book ink.
