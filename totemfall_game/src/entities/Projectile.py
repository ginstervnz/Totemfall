import pygame
import math
import settings
from gale.animation import Animation

class Projectile:
    def __init__(self):
        self.active = False #Pool logic it's false if no proyectile
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.speed = 0
        self.animation = None
        self.texture_id = None

        #Organic move for proyectile
        self.lifetime = 0
        self.nx = 0 
        self.ny = 0 
        self.rotated_frames = []

        #Animation explo magic
        self.is_exploding = False
        self.explosion_timer = 0

    def fire(self, x: float, y: float, angle: float,target_dist: float , config: dict) -> None:
        """
        It wakes up the projectile and injects the configuration (Data-Driven).
        """
        self.active = True
        self.is_exploding = False
        self.x = x
        self.y = y
        self.speed = config.get('speed', 250)
        self.texture_id = config.get('texture', 'magic_bolt')
        

        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

        self.nx = -math.sin(angle)
        self.ny = math.cos(angle)

        waves = max(1, round(target_dist / 30))
        self.wobble_frequency = (math.pi * waves) / target_dist

        angle_deg = math.degrees(-angle) 
        self.rotated_frames = []
        frames_list = config.get('frames', [0, 1, 2, 3])
        
        image = settings.TEXTURES[self.texture_id]
        for frame_idx in frames_list:
            frame_rect = settings.FRAMES[f"{self.texture_id}_frames"][frame_idx]
            surf = image.subsurface(frame_rect)
            rotated_surf = pygame.transform.rotate(surf, angle_deg)
            self.rotated_frames.append(rotated_surf)

        self.animation = Animation(list(range(len(frames_list))), 0.1)

    def explode(self) -> None:
        self.is_exploding = True
        self.dx = 0
        self.dy = 0
        self.explosion_timer = 0.15 
        self.texture_id = 'magic_explosion'
        self.animation = Animation([0, 1, 2, 3], 0.05)



    def update(self, dt: float) -> None:
        # If the bullet is inactive, we skip all its code to save memory.
        if not self.active:
            return

        if self.is_exploding:
            self.explosion_timer -= dt
            self.animation.update(dt)
            if self.explosion_timer <= 0:
                self.active = False
            return

        self.lifetime += dt
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.animation.update(dt)
        #False if proyectile comes off the screen
        margin = 30
        if (self.x < -margin or self.x > settings.VIRTUAL_WIDTH + margin or
            self.y < -margin or self.y > settings.VIRTUAL_HEIGHT + margin):
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        if self.is_exploding:
            image = settings.TEXTURES[self.texture_id]
            frame_idx = self.animation.get_current_frame()
            frame_rect = settings.FRAMES[f"{self.texture_id}_frames"][frame_idx] 
            current_surf = image.subsurface(frame_rect)
            rect = current_surf.get_rect(center=(self.x, self.y))
            surface.blit(current_surf, rect)
            return


        distance_traveled = self.lifetime * self.speed
        wobble = math.sin(distance_traveled * self.wobble_frequency) * 3
        render_x = self.x + (self.nx * wobble)
        render_y = self.y + (self.ny * wobble)
        frame_idx = self.animation.get_current_frame()
        current_surf = self.rotated_frames[frame_idx]
        rect = current_surf.get_rect(center=(render_x, render_y))
        surface.blit(current_surf, rect)