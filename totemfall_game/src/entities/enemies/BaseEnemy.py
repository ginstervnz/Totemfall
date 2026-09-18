import pygame
import settings
import random
from src.world.Pathfinder  import Pathfinder

class BaseEnemy:
    def __init__(self, x: float, y: float, hp: int, speed: float):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 0
        self.hp = hp
        self.speed = speed
        
        self.animations = {}
        self.current_animation = None
        self.state_machine = None
        self.is_dead = False

        self.hit_flash_timer = 0

        self.stuck_attempts = 0
        self.block_to_break = None

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        self.hit_flash_timer = 0.1
        # Debug: print(f"¡Impacto! HP restante: {self.hp}")
        
        if self.hp <= 0:
            self.is_dead = True
            # Debug: print("¡Enemigo derrotado!")


    def _move_with_collisions(self, move_x: float, move_y: float) -> None:
        """Physics engine with a standardized hitbox (12x10) at the enemy's feet."""

        # We store the desired actual speed (magnitude of the vector).
        original_speed = (move_x**2 + move_y**2)**0.5
        if original_speed == 0:
            return

        # We define a fixed physical hitbox that always fits through 16x14 corridors.
        hitbox_w = 12
        hitbox_h = 10
        
        # We obtain the actual size of the chart (with a default 16px margin).
        sprite_w = self.width if hasattr(self, 'width') and self.width > 0 else 16
        sprite_h = self.height if hasattr(self, 'height') and self.height > 0 else 16

        # We calculate the offset so that the small hitbox is positioned at the CENTER and at the FEET.
        offset_x = (sprite_w - hitbox_w) / 2
        offset_y = sprite_h - hitbox_h
        
        # Move in X
        self.x += move_x
        hitbox = pygame.Rect(round(self.x + offset_x), round(self.y + offset_y), hitbox_w, hitbox_h)

        collided_x = False
        if hasattr(self, 'solid_rects'):
            # Loop for processing complex collisions (such as corners or spawning inside a wall)
            idx = hitbox.collidelist(self.solid_rects)
            if idx != -1:
                collided_x = True
                wall = self.solid_rects[idx]
                if move_x > 0: 
                    hitbox.right = wall.left
                elif move_x < 0: 
                    hitbox.left = wall.right
                    
                # Synchronize the floating position based on the hitbox.
                self.x = hitbox.x - offset_x

        if collided_x and move_y != 0:
            move_y = original_speed if move_y > 0 else -original_speed

        # Move in Y
        self.y += move_y
        hitbox.y = round(self.y + offset_y)

        collided_y = False
        if hasattr(self, 'solid_rects'):
            if hasattr(self, 'solid_rects'):
                idx = hitbox.collidelist(self.solid_rects)
                if idx != -1:
                    collided_y = True
                    wall = self.solid_rects[idx]
                    if move_y > 0: 
                        hitbox.bottom = wall.top
                    elif move_y < 0: 
                        hitbox.top = wall.bottom

                    # Synchronize the floating position.
                    self.y = hitbox.y - offset_y

                    
                    # If we hit a horizontal wall (but the X-axis was clear), we redirect the energy to the X-axis.
                    if not collided_x and move_x != 0:
                        extra_x = (original_speed - abs(move_x)) if move_x > 0 else -(original_speed - abs(move_x))
                        self.x += extra_x

                        # Quick safety check for that extra push
                        hitbox.x = round(self.x + offset_x)
                        idx2 = hitbox.collidelist(self.solid_rects)
                        if idx2 != -1:
                            wall2 = self.solid_rects[idx2]
                            if extra_x > 0: hitbox.right = wall2.left
                            elif extra_x < 0: hitbox.left = wall2.right
                            self.x = hitbox.x - offset_x

    def update(self, dt: float) -> None:
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # CPU anti-saturation timer
        if not hasattr(self, 'path_cooldown'):
            self.path_cooldown = 0.0

        if self.path_cooldown > 0:
            self.path_cooldown -= dt
        else:
            if hasattr(self, 'current_path'):
                self.current_path = []

        sprite_w = self.width if hasattr(self, 'width') and self.width > 0 else 16
        sprite_h = self.height if hasattr(self, 'height') and self.height > 0 else 16
        feet_x = self.x + (sprite_w / 2)
        feet_y = self.y + sprite_h - 5

        # We only look for a route if we don't have one and the timer allows it.
        if hasattr(self, 'pathfinder') and hasattr(self, 'target') and self.target:
                if (not hasattr(self, 'current_path') or len(self.current_path) == 0) and self.path_cooldown <= 0:
                    target_w = getattr(self.target, 'width', 0)
                    target_h = getattr(self.target, 'height', 0)
                    target_cx = self.target.x + (target_w / 2)
                    target_cy = self.target.y + target_h - 5
                    self.current_path = self.pathfinder.get_path(feet_x, feet_y, target_cx, target_cy)

                    # If A* returns an empty result (it is trapped), we wait 1 second to avoid burning out the CPU.
                    if not self.current_path:
                        self.path_cooldown = 1.0
                        self.stuck_attempts += 1
                        if self.stuck_attempts >= 2:
                            self._try_break_wall()
                            self.stuck_attempts = 0
                    else:
                        self.stuck_attempts = 0
                        self.path_cooldown = 0.5
        moved_this_frame = False

        # Navigate using the path (Breadcrumbs)
        if hasattr(self, 'current_path') and self.current_path:
            next_waypoint = self.current_path[0]
            dx = next_waypoint[0] - feet_x
            dy = next_waypoint[1] - feet_y
            dist = (dx**2 + dy**2)**0.5
            
            if dist < 4.0 or (self.speed * dt) >= dist:
                self.current_path.pop(0)

            # If nodes remain after deletion, we move smoothly to the next one.
            if len(self.current_path) > 0:
                next_waypoint = self.current_path[0]
                dx = next_waypoint[0] - feet_x
                dy = next_waypoint[1] - feet_y
                dist = (dx**2 + dy**2)**0.5
                
                if dist > 0:
                    move_x = (dx / dist) * self.speed * dt
                    move_y = (dy / dist) * self.speed * dt
                    self._move_with_collisions(move_x, move_y)
                    moved_this_frame = True

        # Plan B (Survival Instinct straight to the Totem)
        if not moved_this_frame and hasattr(self, 'target') and self.target:
            if not hasattr(self, 'current_path') or len(self.current_path) == 0:
                target_w = getattr(self.target, 'width', 0)
                target_h = getattr(self.target, 'height', 0)
                target_cx = self.target.x + (target_w / 2)
                target_cy = self.target.y + target_h - 5
                
                dx = target_cx - feet_x
                dy = target_cy - feet_y
                dist = (dx**2 + dy**2)**0.5
                
                if dist > 15.0:
                    move_x = (dx / dist) * self.speed * dt
                    move_y = (dy / dist) * self.speed * dt
                    self._move_with_collisions(move_x, move_y)

        if self.state_machine:
            self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)


    def _try_break_wall(self) -> None:
        """Scan the adjacent blocks and choose a valid one to break."""
        # We calculate which column and row the enemy is standing in.
        col = int((self.x - settings.MAP_RENDER_OFFSET_X) // settings.TILE_SIZE)
        row = int((self.y - settings.MAP_RENDER_OFFSET_Y) // settings.TILE_SIZE_Y)

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions) # Randomize so it doesn't always break upwards.

        for dx, dy in directions:
            target_col = col + dx
            target_row = row + dy

            # Verify that we are within the map boundaries.
            if 0 <= target_col < settings.MAP_WIDTH and 0 <= target_row < settings.MAP_HEIGHT:
                
                # RESTRICTION 1: Breaking the bottom edge (and consequently, its corners) is prohibited.
                if target_row >= settings.MAP_HEIGHT - 1:
                    continue
                # RESTRICTION 2: Breaking the side edges (left/right corners) is prohibited.
                if target_col == 0 or target_col == settings.MAP_WIDTH - 1:
                    continue
                # RESTRICTION 3: Breaking the overhead protective roof (HUD) is prohibited.
                if target_row <= 3:
                    continue

                # If it passes the tests and is a solid block, we send the signal to break it.
                if self.pathfinder.room.grid[target_row][target_col]:
                    self.block_to_break = (target_col, target_row)
                    break

    def scale_stats(self, level: int) -> None:
        """
        Scales with initial weakness.
        Level 1: Starts at ~45% of base stats.
        Level 12: Reaches 100% of original power.
        High levels: Grows exponentially.
        """
        hp_multiplier = 0.4 + (level * 0.05)
        speed_multiplier = 0.7 + (level * 0.02)
        
        # Scale HP
        original_hp = getattr(self, 'hp', 10)
        self.max_hp = max(1, int(original_hp * hp_multiplier))
        self.hp = self.max_hp
        
        # Scale Speed
        original_speed = getattr(self, 'speed', 20)
        self.speed = min(150, original_speed * speed_multiplier)

        # Ensure they all have a base damage stat to scale (Melee and Ranged)
        if not hasattr(self, 'damage'):
            self.damage = 1 # Give ranged units a base damage stat

        damage_multiplier = 0.5 + (level * 0.03)
        self.damage = max(1, int(self.damage * damage_multiplier))


    def render(self, surface: pygame.Surface, texture_id: str, frames_id: str) -> None:
        if not self.current_animation: return
        
       
        image = settings.TEXTURES[texture_id]
        frame_idx = self.current_animation.get_current_frame()
        frame_rect = settings.FRAMES[frames_id][frame_idx]
        
        enemy_surface = image.subsurface(frame_rect).copy()
    
        if self.hit_flash_timer > 0:
            enemy_surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        
        surface.blit(enemy_surface, (self.x, self.y))

        if self.state_machine and self.state_machine.current:
            render_method = getattr(self.state_machine.current, "render", None)
            if callable(render_method):
                render_method(surface)