import random
import settings
import pygame


class WaveManager:
    def __init__(self, enemy_list: list, totem,current_room) -> None:
        # We hold a reference to the PlayState's enemy list and totem
        self.enemy_list = enemy_list
        self.totem = totem
        self.current_room = current_room
        self.is_active = False

        # Progression stats
        self.global_level = 1
        self.internal_level = 1
        self.world_index = 0
        
        self.total_waves = 1
        self.current_wave_index = 0
        
        self.enemies_to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0 
        self.hp_multiplier = 1.0
        
    def start_level_sequence(self, global_level: int) -> None:
        """Initializes the logic for the entire level, calculating global difficulty."""
        self.global_level = global_level
        self.world_index = (global_level - 1) // 8
        self.internal_level = ((global_level - 1) % 8) + 1 
        
        # Pacing math: Maximum 3 waves per level
        # Levels 1-2: 1 Wave | Levels 3-5: 2 Waves | Levels 6-8: 3 Waves
        self.total_waves = min(3, 1 + (self.internal_level // 3))
        self.current_wave_index = 0
        
        # Stat scaling: +50% health for each new world
        self.hp_multiplier = 1.0 + (self.world_index * 0.5)
        
        # Trigger the first wave of the level
        self.start_next_wave()

    def start_next_wave(self) -> None:
        """Configures the enemies for the ongoing individual wave."""
        self.current_wave_index += 1
        self.is_active = True

        # Increases by 2 enemies per level.
        base_level_enemies = 4 + (self.internal_level * 2)

        # We divide the budget by the number of waves in the level.
        enemies_per_wave = base_level_enemies // self.total_waves

        # We assign the enemies, adding a bonus based on the wave number.
        self.enemies_to_spawn = enemies_per_wave + self.current_wave_index
        
        self.spawn_interval = max(0.6, 2.0 - (self.internal_level * 0.1))
        self.spawn_timer = 1.5 # Dramatic pause of 1.5s before the wave starts

    def update(self, dt: float) -> None:
        """Handles the spawn timer and transition between consecutive waves."""
        if not self.is_active:
            return
            
        self.spawn_timer -= dt
        
        if self.spawn_timer <= 0 and self.enemies_to_spawn > 0:
            self.spawn_enemy()
            self.enemies_to_spawn -= 1
            self.spawn_timer = self.spawn_interval
            
        # WAVE VICTORY CONDITION: Check if wave is completely cleared
        if self.enemies_to_spawn <= 0 and len(self.enemy_list) == 0:
            if self.current_wave_index < self.total_waves:
                # Transition to the next wave within the same level
                self.start_next_wave()
            else:
                # The entire level is completely cleared
                self.is_active = False
            
    def spawn_enemy(self) -> None:
        """Creates an enemy at a random safe location inside the arena boundaries."""
        
        if not hasattr(self.current_room, 'allowed_enemies') or not self.current_room.allowed_enemies:
            return # Safety check if the room doesn't have enemies configured
            
        enemy_class = random.choice(self.current_room.allowed_enemies)
        
        # Instantiate the enemy temporarily at (0,0) to get its width and height
        # SAFEGUARD: Try to inject hp_multiplier, fallback if teammate hasn't updated BaseEnemy yet
        try:
            new_enemy = enemy_class(0, 0, hp_multiplier=self.hp_multiplier)
        except TypeError:
            new_enemy = enemy_class(0, 0)
        
        # Get all the solid blocks from the room to check for collisions
        solid_rects = self.current_room.get_solid_rects()
        
        valid_spawn = False
        max_attempts = 50 # Prevent infinite loops if the map is completely full

        # Use the feet hitbox for the spawn test.
        sprite_w = new_enemy.width if hasattr(new_enemy, 'width') and new_enemy.width > 0 else 16
        sprite_h = new_enemy.height if hasattr(new_enemy, 'height') and new_enemy.height > 0 else 16
        hitbox_w = 12
        hitbox_h = 10
        offset_x = (sprite_w - hitbox_w) / 2
        offset_y = sprite_h - hitbox_h
        
        # Try to find a random spot that doesn't collide with walls
        for _ in range(max_attempts):
            test_x = random.randint(32, settings.VIRTUAL_WIDTH - 32 - sprite_w)
            test_y = random.randint(80, settings.VIRTUAL_HEIGHT - 32 - sprite_h)
            
            # Create a virtual hitbox for testing
            test_rect = pygame.Rect(test_x + offset_x, test_y + offset_y, hitbox_w, hitbox_h)
            
            # collidelist returns -1 if the rect does NOT touch any solid block
            if test_rect.collidelist(solid_rects) == -1:
                spawn_x = test_x
                spawn_y = test_y
                valid_spawn = True
                break
                
        # If we found a valid spot, place the enemy and activate it
        if valid_spawn:
            new_enemy.x = spawn_x
            new_enemy.y = spawn_y
            new_enemy.target = self.totem
            self.enemy_list.append(new_enemy)