# Changelog - Totemfall

All additions, changes, and fixes for this project will be documented in this file.

## [v0.1.0] - Base Structure and Player Movement

### Added
- **Virtual Environment and Framework:** Initial project setup using Pygame and the Gale framework.
- **State Machine (Game States):** Implementation of core state architecture (`MainMenuState`, `PlayState`, `OptionsState`) for a clean game flow.
- **Independent Player Entity:** Creation of the `Player` class using its own state machine (`PlayerIdleState`, `PlayerWalkState`).
- **Animation System:** Integration of `gale.animation` to smoothly play wizard sprites (idle and walk) based on a precise 26x18 pixel grid.
- **Level Rendering:** Implementation of the defense platform (`sprStairs.png`) at the top of `PlayState`, reserving space (HUD) for the future interface.
- **Tactical Cursor:** Hidden the native Windows cursor and replaced it with a custom crosshair (`sprCursor.png`) that follows the mouse using scaled virtual coordinates.
- **Shooting Math (Fundamentals):** Incorporation of trigonometric logic (`math.atan2`) to calculate the exact angle between the player's center and the mouse cursor, laying the groundwork for the projectile *Object Pooling* system.

### Changed
- **System Controls:** Removed accidental game exit via the `ESC` key. Pressing the `Ctrl + Q` key combination is now required to safely close the application.

## [v0.2.0] - Combat System, AI, and Game Feel

### Added
- **Collision System (Hitboxes):** Implementation of physics logic between entities (enemies, projectiles, and structures) to register hits.
- **Particle Effects (Blood):** Integration of the Gale framework's `ParticleSystem` to emit directional blood splatters when damage is registered on enemies.
- **Visual Feedback (Game Feel):** Addition of white flashes upon taking damage using color saturation (`BLEND_RGB_ADD`) and state transitions in projectiles to trigger explosion animations on impact.
- **Melee AI (Batilisk):** Creation of the `Batilisk` entity featuring mathematical pursuit logic (pathfinding), a dedicated attack state (`EnemyAttackState`), and a sword-slash visual effect that dynamically calculates and rotates toward the target.
- **Ranged AI (Goblin):** Creation of the `Goblin` archer entity with its own independent arrow *Object Pool*.
- **Range and Movement Logic (Strafing):** Implementation of `EnemyRangedWalkState` to calculate Euclidean distances (vision range), and `EnemyRangedAttackState` featuring strafing behavior and tactical pauses for drawing the bow, preventing the enemy from being a static target.

## Procedural Generation, Multi-worlds, and Physics

### Added
- **Base Procedural Architecture:** Created the `ProceduralRoom` parent class responsible for generating level structures.
- **Map Algorithms:** Implemented *Path Carving* (ensuring escape routes), Cellular Automata (smoothing to fill in trap-like gaps), and Clustering (organic block grouping).
- **Arena Clearing:** Mathematical logic to keep the map center and corners clear, prioritizing space for combat.
- **Multi-world System:** Created 5 distinct environments (`SwampRoom`, `InfernoRoom`, `CatacombsRoom`, `RockRoom`, `WaterRoom`) using object-oriented inheritance (DRY principle) to inherit procedural logic while injecting unique textures.
- **Modular Progression:** Implemented a level manager in `PlayState` that increases obstacle density from level 1 to 8 and automatically switches worlds using the modulo operator (`%`).
- **Dynamic Projectile Physics:** Added the `get_collision_rect()` method to projectiles to calculate real-time dynamic hitboxes that account for rotation and wave patterns ("wobble").
- **AABB Collision Detection:** Magic projectiles now correctly detect solid blocks and deactivate (destroy themselves) upon impact with arena walls.
- **Debounce Timer:** Included an input cooldown to prevent single touches from registering multiple keystrokes (key bouncing) during level transitions.

### Changed
- **Refactoring and Optimization:** Optimized the complexity of map spatial matrix generation by merging nested loops and utilizing *Set Comprehensions* (fast, native Python operations). - **Visual Padding Adjustment:** Mathematical modification of `TILE_SIZE_Y` in the global settings to squash the sprites and eliminate transparent gaps, resulting in visually solid, connected walls.

## [v0.3.0] - Enemy Spawning, Totem Health, and Initial Waves

### Added
- **Procedural Enemy Spawning Architecture:** Created the `WaveManager.py` class to manage enemy spawning within the level.
- **Enemy Map Algorithms:** Implemented specific enemy types based on the world type.
- **Enemy Type Integration:** Implemented the various monster types featured in the game.


## [v0.4.0] - Cutscenes, Advanced Physics, and Statistics (Kill Tracker)

### Added
- **Level Cutscenes:** Implemented victory sequences (ascension to the sky) and triumphant entries (landing in the new level) using the mathematical interpolation engine (`Timer.tween`).
- **Transition Effect (Iris Wipe):** A visual circular closing and opening system between scenes, built using the Pygame surface and color-key masking (`set_colorkey`).
- **Defeat Cutscene (Time Freeze):** Implemented a "Time Freeze" pattern that halts engine logic to execute a particle explosion and the sinking of the Totem before the state change.
- **Statistics System (Kill Tracker):** Dynamic kill tracking using a dictionary (`kill_counts`) that identifies defeated monster types via their `texture_id` attribute.
- **Dynamic Grid UI (Grid Layout):** Mathematically redesigned the `GameOverState` to organize the kill report into a self-centering grid (up to 7 columns), capable of scaling and displaying multiple sprites and text multipliers ("x N") without overlapping.

### Changed
- **Weapon Safety System:** Implemented a communication flag (`can_shoot`) between `PlayState` and `Player` to suspend mana consumption, blocking shots during cutscenes or when no enemies are present. - **Rendering and Particle Lifespan:**

### Fixed
- **Wall Sliding:** Redesigned the `_move_with_collisions` physics engine in `BaseEnemy` by applying momentum conservation. Enemies now transfer 100% of their acceleration to the free axis, eliminating artificial speed loss (wall friction).
- **Target Jittering:** Incorporated an "Attack Radius" (15-pixel stopping distance) into the survival algorithm (Plan B). Melee monsters now come to a dead stop when surrounding the Totem, eliminating AABB collision jitter.
- **Instant Projectile Cleanup:** Resolved the "ghost fire" issue by forcibly destroying any active on-screen missiles the exact millisecond a cutscene begins.
- **Card Types Added:** Implemented various card types that grant powers to the player.

## Summoning System, UI "Juice," and Visual Effects

### Added
- **Card UI Effects ("Juice"):** Implemented entry animations (tweening), dynamic scaling with a gold border on hover, integrated magic particles, and intelligent auto-adjusting text.
- **Time Manipulation (Slow-Mo):** Added a time-dilation effect that slows down the action when selecting an upgrade and gradually restores speed upon resuming combat.
- **Animated XP Vortices:** Created XP orbs using animated textures via the framework's animation system.
- **Ally Summoning System:** Created the `Ally.py` proxy class, capable of cloning any enemy from the current level and overriding its AI to defend the player (marked with a blue diamond). - **Evolving Card Deck:** The card manager now applies advanced options (bonus damage for allies and extra summon slots) only after the player unlocks the base ability.
- **Tactical Defensive Formations:** Allied monsters switch to "Guardian Mode," moving to pre-set escort positions in front of the obelisk once the wave is cleared.
- **Dynamic Aggro and Interception System:** Enemies assess distance in real-time to prioritize engaging the nearest allies rather than the obelisk. Enemy projectiles now also hit and damage summons.
- **Spawn Drop Animations:** Both enemies and allies enter the battlefield by dropping from the sky with a bounce effect, triggering a new impact particle system (`DustEffect.py`) upon hitting the ground.


## [v0.5.0] - Persistence, Global Leaderboard, and Infinite Mode

### Added
- **Local Data Persistence:** Implementation of the `json` module within global configurations to read and write a `save_data.json` file, storing the player's name on the hard drive.
- **Arcade-Style Player Registration:** Creation of `NameInputState`, an interface allowing users to enter a 5-letter name using keyboard navigation (arrow keys and Enter), emulating classic arcade machines.
- **Global Leaderboard Integration (Dreamlo):** Native HTTP connection to the Dreamlo API for submitting and retrieving scores. The process runs on a background thread (`threading`) during `GameOverState` and `VictoryState` to prevent rendering blocks (frame freezing).
- **Dynamic Main Menu Background:** Integration of a background image (`menu_bg`) that automatically scales to the game's virtual resolution. A semi-transparent dark overlay (`SRCALPHA` with 100 opacity) was applied over the background to ensure menu text readability and contrast.
- **Survival Mode (Infinite/Random):** A new post-victory feature ("Keep Playing") that injects a flag (`random_mode`) into `PlayState`. This alters level generation to load random worlds (1 through 40), standardizes point gains (fixed 100 pts per kill), and changes the HUD indicator to "Level: INF," while preserving the player's previous progress.
- **Horizontal Submenus:** Architectural redesign of end-game screens to support X-axis options; positions are dynamically calculated at 35% and 70% of the screen width, with `Left`/`Right` key mapping implemented. - **Operating System Customization:** Integration of the native `pygame.display.set_icon()` function to dynamically inject a game sprite (the wizard) as the system window icon, alongside parameterization of the application title.

### Changed
- **Main Menu Expansion:** Restructured the option list and routing for `MainMenuState`. Players can now navigate between four full options: *Play* (starts the game), *Global Top* (connects to the Dreamlo API), *Change Name* (modifies the persistence `.json` file), and *Exit* (safely closes the game).
- **Navigation Standardization:** Corrected the mathematical direction of the cursor in `MainMenuState` to align with UX standards.

## Advanced Cinematics, Dynamic Environments, and Audio Polish

### Added
- **Introductory Cinematic (`IntroCinematicState`):** Created a brand-new state orchestrated using `gale.timer` and `gale.animation`. It features a massive horde of scaled, offset monsters chasing the player, complete with dynamic dust particles and a hard cut transition to gameplay.
- **Massive Invisible Walls (World Bounds):** Procedural injection of four colossal, invisible blocks (500px thick) surrounding the game grid. This definitively prevents "soft-locking" caused by entities being spawned or pushed outside the render area by the collision engine.
- **Hybrid Safe-Spawn System:** The `WaveManager` algorithm now combines logical grid constraints with full AABB physical collision checks, ensuring that bulky enemies do not have their hitboxes overlap with wall textures.
- **Demolition Mechanic (Block Destruction):** Implemented the `BlocksCard` and associated audio feedback. Players can now dynamically shoot and destroy procedurally generated walls (while respecting perimeter boundaries), altering AI pathfinding in real-time.
- **Seamless Audio Orchestration:** Adjusted `settings.AUDIO_MANAGER` to handle asynchronous stopping and cross-fading (fade-out) for both the new chase sound effect (`chase.ogg`) and the obelisk collapse (`totemfall.ogg`) during their respective state transitions.

### Changed
- **Lethal Boundary Extension (Insta-Kill Failsafe):** Mathematically adjusted the failsafe tolerance margin (+32px) to prevent the accidental deletion of larger monster models as they attempt to navigate around the map boundaries. - **Dynamic Stat Scaling:** Full integration of the `scale_stats` function into the `WaveManager` horde spawning routine, scaling each unit's health and speed in real-time based on the global level.

## [v0.5.5] - Horde Acceleration, Electric Mechanics, and Shield System

### Added
- **Art Credits Screen (`CreditsState`):** Implementation of a new vertically scrolling text interface, accessible from the main menu. Designed to formally credit asset creators (Reaktori, Batareya, and Atelier Pixerelia), it manages dynamic spacing based on line count and uses top-center anchoring (`midtop`) to prevent text clipping at low resolutions.
- **Gradual Crowd Control Limiter:** A dynamic mathematical barrier was added to the wave manager; it temporarily halts enemy spawning if the player fails to clear the screen quickly enough. In early levels, this enforces controlled, gradual combat, but the limit expands exponentially at higher levels, allowing for massive assaults.
- **Dynamic Horde Burst Spawning:** Replaced the traditional rhythmic timer with a stochastic spawning system. The engine now summons random clusters (*bursts*) of simultaneous monsters and varies the timing interval between 50% and 150%, creating organic, unpredictable pressure at high levels.
- **Chain Volt Mechanic:** Introduction of a new card evolution path. It grants the player charged projectiles that, upon detonation, perform a Euclidean scan of surrounding enemies and propagate branching damage.
- **Procedural Electricity VFX:** Development of the `LightningEffect` system. It utilizes pure rendering via Pygame primitives (`pygame.draw.lines`) to generate irregular, dynamic, high-voltage electric arcs, connecting impact vectors without using pre-rendered sprites or consuming texture memory. - **Temporary Shield Mechanic (Aegis):** Integration of an ultimate card that grants the obelisk a cyclical immunity property. It generates a procedural, unstable energy shield calculated parametrically from the center of the Totem.
- **Forced Immunity Reset:** Implementation of a strict reset (`reset_shield`) upon leveling up to ensure the *Aegis* ability's cyclical timer is neither carried over nor manipulated during transition cutscenes.

### Changed
- **Mathematical Global Scaling:** Restructured the budget formula in `WaveManager`. The total enemy count is now calculated based on absolute game progress (`global_level`) rather than resetting per world cycle (`internal_level`), making invasions at level 20+ monumentally overwhelming.
- **Menu Visual Refinement:** Replaced `pygame.transform.scale` with `pygame.transform.smoothscale` for the main menu background (`menu_bg`). A bilinear interpolation filter was applied to preserve smoothness, the original orb glow, and the artwork's high definition when downscaling to the engine's native resolution (480x270 pixels).

### - Architectural Optimization, Smart Caching, and Mana Economy
- **Added** Level Restoration: Modified the `advance_level` method in the main orchestrator to automatically restore 100% of the player's mana when transitioning to a new wave or world.

### Changed
- **Interface Architecture (Smart Caching):** Fully extracted static rendering logic into a new delegate class, `HUD.py`. Implemented a design pattern using `@classmethod` and cache variables to pre-scale textures (`pygame.transform.scale`) and rasterize fonts (`font.render`) once in memory.

- **Visual Effects Decoupling:** Applied the Single Responsibility Principle (SRP) by moving the `BloodEffect`, `DarkSmokeEffect`, and `LightningEffect` classes from the main controller to an independent module (`Effects.py`), improving code reusability.

- **Structural Refactoring (PlayState):** Massively defragmented the main game state. By delegating the GUI and effects, the "God Object" anti-pattern was eliminated, drastically reducing lines of code and stabilizing RAM usage.
