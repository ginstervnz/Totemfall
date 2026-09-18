# Totemfall Game

## Overview & Lore
**Totemfall** is a fast-paced, roguelite action-defense game where you play as a powerful wizard tasked with a single, crucial mission: protecting the sacred Totem from endless hordes of corrupt creatures. Positioned high on an ancient platform, you must cast spells, summon allies, and harness the elements to hold the line against goblins, batilisks, and other monstrous entities trying to destroy the obelisk. As the enemies grow stronger, so does your magical arsenal through a dynamic deck-building upgrade system.

## Academic Context
This game was developed as the final capstone project for the course **Programación de Videojuegos 1** (Video Game Programming 1) at Universidad de Los Andes. It represents a comprehensive application of software architecture, game loops, advanced object-oriented programming, and real-time physics algorithms.

## Core Mechanics & Features
Totemfall blends stationary arcade shooting with deep roguelite progression and procedural elements:
* **Dynamic Wave Pacing:** The game features a custom crowd-control system. Early levels carefully pace enemy spawns to teach the mechanics, while higher levels unleash massive, unpredictable bursts of enemies to test your limits.
* **Procedural Arenas:** Battles take place across 5 distinct biomes (Swamp, Inferno, Catacombs, Rock Room, and Water Room). The terrain is procedurally generated using cellular automata and path-carving algorithms, creating destructible blocks and unique layouts every time.
* **Card-Based Upgrade System:** Upon leveling up from dropped Experience Orbs, time freezes and you are presented with a choice of 3 randomized cards. Upgrades include mana regeneration, attack speed, chain lightning attacks, temporary Aegis shields for the Totem, and more.
* **Ally Summoning:** You can spend mana to summon your own monster variants to the battlefield. These allies intercept enemy projectiles, take aggro, and fight for the Totem.
* **Advanced Combat Physics:** Features fully integrated AABB collision detection, rotational projectile physics, screen shake, slow-motion hits, and procedural visual effects (VFX) like drawn lightning and particle blood bursts.
**Top Global (Dreamlo) Integration:** Native HTTP connection to the Dreamlo API for submitting and retrieving scores—giving players a reason to try and survive more waves.

## Progression & Infinite Mode
The main campaign consists of **40 levels** divided across 5 unique worlds. As you progress, the enemy density and stats scale exponentially. 
* **Victory or Eternity:** Upon clearing Level 40, you are given a choice. You can end your run and claim your well-earned Victory, or you can push beyond the limits into **Infinite Mode**.
* **Infinite Mode:** If you choose to continue, the game removes the level cap. Enemy spawns and stats scale endlessly, worlds are chosen at random, and you fight strictly for survival and a spot on the Global Top leaderboard.

## Controls
Totemfall is designed with an intuitive, mouse-driven combat system:
* **Mouse Movement:** Aim your magical crosshair.Firing automatically, eliminating the need for clicking.
* **Left Mouse Button (UI):** Select upgrade cards during level-ups and navigate the main menu.
* **Arrow Keys / Up & Down:** Alternative navigation for the Main Menu.
* **Enter:** Confirm menu selections.
* **Ctrl + Q:** Quick exit the game safely.

## Technologies Used
* **Python 3:** The core programming language.
* **Pygame:** Used for rendering graphics, handling window events, playing audio, and calculating basic geometry.
* **Gale Framework:** A lightweight game architecture framework used to handle State Machines (managing transitions between menus, gameplay, and game-over screens), particle systems, tweening animations, and input handling.
* **Dreamlo API:** Integrated for live, global high-score tracking in Infinite Mode.

## Installer

The following link is for Windows users: https://drive.google.com/file/d/1p6Wy7_1Fl1oLYp8K9jnCHVVdda9ieoIx/view?usp=sharing
Mac and/or Linux users must clone or download the repository and ensure all required dependencies are installed.