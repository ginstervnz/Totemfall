import pygame
import math

class Ally:
    def __init__(self, x: float, y: float, enemy_template, bonus_damage: int = 0):
        self.visuals = enemy_template
        self.visuals.x = x
        self.visuals.y = y
        self.visuals.speed *= 1.2 
        
        if hasattr(self.visuals, 'damage'):
            self.visuals.damage += bonus_damage
            
        self.is_dead = False

    # --- CRITICAL: These properties ensure the proxy always uses real-time coordinates ---
    @property
    def x(self): return self.visuals.x
    @property
    def y(self): return self.visuals.y
    @property
    def width(self): return self.visuals.width
    @property
    def height(self): return self.visuals.height

    def _find_nearest_enemy(self, enemies: list):
        closest = None
        min_dist = float('inf')
        for enemy in enemies:
            if not getattr(enemy, 'is_dead', False):
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest = enemy
        return closest

    def update(self, dt: float, enemies: list, totem, allies: list) -> None:
        if getattr(self.visuals, 'hp', 0) <= 0:
            self.is_dead = True
            return

        old_target = getattr(self.visuals, 'target', None)
        nearest = self._find_nearest_enemy(enemies)

        if nearest:
            # --- COMBAT MODE ---
            self.visuals.target = nearest
            
            # Unconditionally force 'walk' state if the target changes to prevent swinging at air
            if self.visuals.target != old_target:
                if hasattr(self.visuals, 'state_machine'):
                    self.visuals.state_machine.change('walk')
                        
            # Run their normal AI
            self.visuals.update(dt)
            
        else:
            # --- GUARDIAN MODE (Fixed Front Formation) ---
            self.visuals.target = None 
            
            # FORCE the state machine and animation to 'walk' so they put their weapons away!
            if old_target is not None: 
                if hasattr(self.visuals, 'state_machine'):
                    self.visuals.state_machine.change('walk')
            
            if hasattr(self.visuals, 'hit_flash_timer') and self.visuals.hit_flash_timer > 0:
                self.visuals.hit_flash_timer -= dt
                
            try:
                my_index = allies.index(self)
            except ValueError:
                my_index = 0
                
            offsets = [(0, 50), (-40, 50), (40, 50)]
            my_offset = offsets[my_index % len(offsets)]
            
            totem_cx = totem.x + (totem.width / 2)
            totem_cy = totem.y + (totem.height / 2)
            
            target_x = totem_cx + my_offset[0] - (self.width / 2)
            target_y = totem_cy + my_offset[1] - (self.height / 2)
            
            dist = math.hypot(target_x - self.x, target_y - self.y)
            
            # Move towards assigned formation slot
            if dist > 3:
                move_angle = math.atan2(target_y - self.y, target_x - self.x)
                self.visuals.x += math.cos(move_angle) * self.visuals.speed * dt
                self.visuals.y += math.sin(move_angle) * self.visuals.speed * dt
                self.visuals.facing_right = math.cos(move_angle) > 0
                
                # Manually ensure the walk animation plays while moving to formation
                if hasattr(self.visuals, 'animations') and 'walk' in self.visuals.animations:
                    self.visuals.current_animation = self.visuals.animations['walk']
                    self.visuals.current_animation.update(dt)
            else:
                if my_index == 1:
                    self.visuals.facing_right = False 
                else:
                    self.visuals.facing_right = True 
                    
                # Freeze the animation on the first frame (idle look) when they arrive at formation
                if hasattr(self.visuals, 'animations') and 'walk' in self.visuals.animations:
                    self.visuals.current_animation = self.visuals.animations['walk']
                    self.visuals.current_animation.timer = 0
                    self.visuals.current_animation.current_frame = 0


    def take_damage(self, amount: int) -> None:
        """Proxies the damage to the underlying visual template."""
        if hasattr(self.visuals, 'take_damage'):
            self.visuals.take_damage(amount)
        else:
            self.visuals.hp -= amount


    def render(self, surface: pygame.Surface) -> None:
        self.visuals.render(surface)
        
        # Indicator diamond
        cx = self.x + (self.width / 2)
        top = self.y - 10
        diamond = [(cx, top), (cx + 5, top - 5), (cx, top - 10), (cx - 5, top - 5)]
        pygame.draw.polygon(surface, (50, 200, 255), diamond)