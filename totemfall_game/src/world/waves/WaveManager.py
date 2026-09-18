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
        self.total_waves = min(4, 1 + (self.global_level // 4))
        self.current_wave_index = 0
        
        # Stat scaling: +50% health for each new world
        self.hp_multiplier = 1.0 + (self.world_index * 0.5)
        
        # Trigger the first wave of the level
        self.start_next_wave()

    def start_next_wave(self) -> None:
        """Configures the enemies for the ongoing individual wave."""
        self.current_wave_index += 1
        self.is_active = True

        base_level_enemies = 5 + int(self.global_level * 1.5)
        enemies_per_wave = base_level_enemies // self.total_waves
        self.enemies_to_spawn = enemies_per_wave + self.current_wave_index
        
        # Faster base interval since we are no longer spawning in bursts
        self.spawn_interval = max(0.6, 2.0 - (self.global_level * 0.05))
        self.spawn_timer = 1.5

    def update(self, dt: float) -> None:
        """Handles the spawn timer and transition between consecutive waves."""
        if not self.is_active:
            return
            
        self.spawn_timer -= dt
        
        if self.spawn_timer <= 0 and self.enemies_to_spawn > 0:
            
            # --- STRICT EARLY GAME PACING ---
            if self.global_level <= 3:
                if len(self.enemy_list) >= 1:
                    return 
            elif self.global_level <= 8:
                if len(self.enemy_list) >= 2:
                    return 
            else:
                max_allowed_alive = 2 + (self.global_level // 4)
                if len(self.enemy_list) >= max_allowed_alive:
                    return 
            
            # Spawn strictly ONE enemy at a time to naturally desynchronize their attack timers
            if self.spawn_enemy(): 
                self.enemies_to_spawn -= 1
            
            # Shorter, randomized interval for the next single spawn
            if self.enemies_to_spawn > 0:
                self.spawn_timer = self.spawn_interval * random.uniform(0.7, 1.3)
            
        # WAVE VICTORY CONDITION: Check if wave is completely cleared
        if self.enemies_to_spawn <= 0 and len(self.enemy_list) == 0:
            if self.current_wave_index < self.total_waves:
                self.start_next_wave()
            else:
                self.is_active = False
            
    def spawn_enemy(self) -> bool:
        """Creates an enemy at a valid tile, respecting hitboxes and a safe zone around the Totem."""
        
        if not hasattr(self.current_room, 'allowed_enemies') or not self.current_room.allowed_enemies:
            return False 
            
        enemy_class = random.choice(self.current_room.allowed_enemies)
        
        try:
            new_enemy = enemy_class(0, 0, hp_multiplier=self.hp_multiplier)
        except TypeError:
            new_enemy = enemy_class(0, 0)
        
        if hasattr(self.current_room, 'grid'):
            valid_tiles = []
            solid_rects = self.current_room.get_solid_rects()
            
            for y in range(4, settings.MAP_HEIGHT):
                for x in range(settings.MAP_WIDTH):
                    if not self.current_room.grid[y][x]:
                        valid_tiles.append((x, y))
                        
            random.shuffle(valid_tiles)
            
            sprite_w = new_enemy.width if hasattr(new_enemy, 'width') and new_enemy.width > 0 else 16
            sprite_h = new_enemy.height if hasattr(new_enemy, 'height') and new_enemy.height > 0 else 16
            
            import math
            totem_cx = self.totem.x + (self.totem.width / 2)
            totem_cy = self.totem.y + (self.totem.height / 2)
            valid_spawn = False
            
            for tile_x, tile_y in valid_tiles:
                px = settings.MAP_RENDER_OFFSET_X + tile_x * settings.TILE_SIZE
                py = settings.MAP_RENDER_OFFSET_Y + tile_y * settings.TILE_SIZE_Y
                
                test_x = px + (settings.TILE_SIZE / 2) - (sprite_w / 2)
                test_y = py + (settings.TILE_SIZE_Y / 2) - (sprite_h / 2)
                
                # SAFE ZONE CHECK: Ensure the enemy does not spawn too close to the Totem
                dist_to_totem = math.hypot(test_x + (sprite_w / 2) - totem_cx, test_y + (sprite_h / 2) - totem_cy)
                if dist_to_totem < 100:
                    continue
                
                test_rect = pygame.Rect(test_x, test_y, sprite_w, sprite_h)
                if test_rect.collidelist(solid_rects) == -1:
                    spawn_x = test_x
                    spawn_y = test_y
                    valid_spawn = True
                    break
        else:
            valid_spawn = False 

        if valid_spawn:
            new_enemy.x = spawn_x
            new_enemy.y = spawn_y - 200 
            new_enemy.target = self.totem
            new_enemy.scale_stats(self.global_level)
            self.enemy_list.append(new_enemy)
            new_enemy.is_spawning = True
            
            def on_drop_finish(entity=new_enemy):
                entity.is_spawning = False
                dust_x = entity.x + (entity.width / 2)
                dust_y = entity.y + entity.height
                self.particle_systems.append(DustEffect(dust_x, dust_y))
                
            Timer.tween(0.8, [(new_enemy, {"y": spawn_y})], ease_function_name="out_bounce", on_finish=on_drop_finish)
            return True 
            
        return False