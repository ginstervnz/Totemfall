import random
import settings
import pygame
from gale.timer import Timer
from src.entities.DustEffect import DustEffect



class WaveManager:
    def __init__(self, enemy_list: list, totem,current_room,particle_systems: list) -> None:
        # We hold a reference to the PlayState's enemy list and totem
        self.enemy_list = enemy_list
        self.totem = totem
        self.current_room = current_room
        self.particle_systems = particle_systems
        self.is_active = False
        
        # Wave stats
        self.current_wave = 1
        self.enemies_to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0 
        
    def start_wave(self, wave_number: int) -> None:
        """Configures and starts a new wave."""
        self.current_wave = wave_number
        self.is_active = True
        
        # Simple progression: more enemies per wave
        self.enemies_to_spawn = 4 + (wave_number * 2) 
        
        # The higher the wave, the faster they spawn (minimum 0.8 seconds)
        self.spawn_interval = max(0.8, 2.5 - (wave_number * 0.15))
        self.spawn_timer = 1.0 # First enemy appears after 1 second

    def update(self, dt: float) -> None:
        """Handles the spawn timer and wave completion logic."""
        if not self.is_active:
            return
            
        self.spawn_timer -= dt
        
        if self.spawn_timer <= 0 and self.enemies_to_spawn > 0:
            self.spawn_enemy()
            self.enemies_to_spawn -= 1
            self.spawn_timer = self.spawn_interval
            
        # Check if wave is completely cleared (no enemies left to spawn AND screen is clear)
        if self.enemies_to_spawn <= 0 and len(self.enemy_list) == 0:
            self.is_active = False
            
    def spawn_enemy(self) -> None:
        """Creates an enemy at a random safe location inside the arena boundaries."""
        
        if not hasattr(self.current_room, 'allowed_enemies') or not self.current_room.allowed_enemies:
            return # Safety check if the room doesn't have enemies configured
            
        enemy_class = random.choice(self.current_room.allowed_enemies)
        
        # Instantiate the enemy temporarily at (0,0) to get its width and height
        new_enemy = enemy_class(0, 0)
        
        # Get all the solid blocks from the room to check for collisions
        solid_rects = self.current_room.get_solid_rects()
        
        valid_spawn = False
        max_attempts = 50 # Prevent infinite loops if the map is completely full
        
        spawn_x = 0
        spawn_y = 0
        
        # Try to find a random spot that doesn't collide with walls
        for _ in range(max_attempts):
            # Generate random X and Y inside the valid arena space.
            # We offset by ~32 pixels to avoid spawning exactly on the border walls.
            # Y starts at 80 to avoid spawning inside the top UI/Totem area.
            test_x = random.randint(32, settings.VIRTUAL_WIDTH - 32 - new_enemy.width)
            test_y = random.randint(80, settings.VIRTUAL_HEIGHT - 32 - new_enemy.height)
            
            # Create a virtual hitbox for testing
            test_rect = pygame.Rect(test_x, test_y, new_enemy.width, new_enemy.height)
            
            # collidelist returns -1 if the rect does NOT touch any solid block
            if test_rect.collidelist(solid_rects) == -1:
                spawn_x = test_x
                spawn_y = test_y
                valid_spawn = True
                break
                
        # If we found a valid spot, place the enemy and activate it
        if valid_spawn:
            new_enemy.x = spawn_x
            new_enemy.y = spawn_y - 200 # Spawn high in the sky
            new_enemy.target = self.totem
            self.enemy_list.append(new_enemy)
            new_enemy.is_spawning = True
            def on_drop_finish(entity=new_enemy):
                entity.is_spawning = False
                dust_x = entity.x + (entity.width / 2)
                dust_y = entity.y + entity.height
                self.particle_systems.append(DustEffect(dust_x, dust_y))
            # JUICE: ENEMY SPAWN DROP 
            Timer.tween(0.8, [(new_enemy, {"y": spawn_y})], ease_function_name="out_bounce", on_finish=on_drop_finish)
        