import pygame
import random
import math
import settings
from gale.animation import Animation

class Totem:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 38
        self.height = 48
        self.animation = Animation(list(range(14)), 0.15)

        #Heal
        self.max_hp = 5
        self.hp = self.max_hp
        self.hit_flash_timer = 0

        # CINEMATIC SHAKE TIMER
        self.shake_timer = 0.0

        # --- SHIELD MECHANIC ---
        self.has_shield_ability = False
        self.shield_active = False
        self.shield_cooldown = 12.0
        self.shield_cooldown_max = 12.0
        self.shield_duration = 0.0
        self.shield_duration_max = 2.5
        self.shield_points = []


    def reset_shield(self) -> None:
        """Forces the shield into cooldown mode when entering a new level."""
        self.shield_active = False
        self.shield_cooldown = self.shield_cooldown_max
        self.shield_duration = 0.0

    def take_damage(self, amount: int) -> None:
        # INVULNERABILITY CHECK 

        if getattr(self, 'shield_active', False):
            import settings
            if 'hit_wall' in settings.AUDIO_MANAGER.sounds:
                settings.AUDIO_MANAGER.play_sfx('hit_wall') # Feedback for blocked damage
            return 
        
        self.hp = max(0, self.hp - amount)
        self.hit_flash_timer = 0.15

    def update(self, dt: float) -> None:
        self.animation.update(dt)

        # Heal
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

        # UPDATE SHAKE 
        if self.shake_timer > 0:
            self.shake_timer -= dt

        # SHIELD TIMER LOGIC
        if getattr(self, 'has_shield_ability', False):
            if self.shield_active:
                self.shield_duration -= dt
                self.shield_points = []
                cx = self.x + (self.width / 2)
                cy = self.y + (self.height / 2)
                base_radius = 28 # Size of the shield
                
                segments = 12
                for i in range(segments):
                    angle = (i / segments) * math.pi * 2
                    # Randomize the radius slightly to make it look like unstable energy
                    r = base_radius + random.uniform(-4, 4)
                    px = cx + math.cos(angle) * r
                    py = cy + math.sin(angle) * r
                    self.shield_points.append((px, py))
                
                if self.shield_duration <= 0:
                    self.shield_active = False
                    self.shield_cooldown = self.shield_cooldown_max
            else:
                self.shield_cooldown -= dt
                if self.shield_cooldown <= 0:
                    self.shield_active = True
                    self.shield_duration = self.shield_duration_max
                    

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['obelisk']
        frame_idx = self.animation.get_current_frame()
        frame_rect = settings.FRAMES['obelisk_frames'][frame_idx]
        
        entity_surface = image.subsurface(frame_rect).copy() 
                
        if self.hit_flash_timer > 0:
            entity_surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)

        # APPLY SHAKE OFFSET ON RENDER 
        render_x = self.x
        render_y = self.y
        if self.shake_timer > 0:
            render_x += random.randint(-10, 10)
            render_y += random.randint(-10, 10)

                    
        surface.blit(entity_surface, (render_x, render_y))

        # SHIELD RENDER 
        if getattr(self, 'shield_active', False) and len(self.shield_points) > 2:
            # Draw the closed jagged polygon. True means the loop closes automatically.
            pygame.draw.lines(surface, (0, 255, 255), True, self.shield_points, 2)
            pygame.draw.lines(surface, (255, 255, 255), True, self.shield_points, 1)