# Domain Glossary: Alex-Survive 📖

Canonical terminology for entities, systems, items, and state models in the Alex-Survive project. All code, scenes, resources, and tests should strictly use these terms.

---

## 1. Entities & Characters

- **Alex (`Player`)**: The playable survivor character. Uses `CharacterBody3D` with third-person locomotion, stamina management, and inventory.
- **Infected (`Enemy`)**: The overarching term for all undead enemies. Sub-types:
  - **`Walker`**: Standard slow-moving infected that shuffles toward targets and claws at barricades.
  - **`Runner`**: High-speed, agile infected that sprints, leaps, and flanks.
  - **`Brute`**: Bulky, muscular infected miniboss that breaks barricades with heavy blows.
  - **`Tank`**: Heavily mutated, colossal infected boss with immense health and ground-smash attacks.
- **Wildlife (`Fauna`)**: Non-hostile or skittish animals roaming the outer perimeter (`Rabbit`, `Deer`).
- **Fish (`FishSpot`)**: Interactable fishing point along the creek/river.

---

## 2. Survival Systems & Vitals

- **Health (`hp`)**: Hit points of player or entities. Dropping to zero triggers entity death or game over.
- **Stamina (`stamina`)**: Energy pool depleted by sprint, dodge, and melee attacks; regenerates when idle or walking.
- **Hunger (`hunger`)**: Metabolic stat depleted over time; thresholds affect stamina recovery rate and damage output.
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
