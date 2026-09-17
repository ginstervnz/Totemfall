import pygame
import math
import settings
from gale.animation import Animation

class Projectile:
    def __init__(self):
        self.active = False #Pool logic it's false if no proyectile
        self.is_electric = False
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.speed = 0
        self.width = 0
        self.height = 0
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
        self.is_electric = config.get('is_electric', False)
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

        base_rect = settings.FRAMES[f"{self.texture_id}_frames"][frames_list[0]]
        self.width = base_rect.width
        self.height = base_rect.height

        self.animation = Animation(list(range(len(frames_list))), 0.1)

    def explode(self, texture_id='magic_explosion', frames=None, frame_time=0.05) -> None:
        if frames is None:
            frames = [0, 1, 2, 3] 
        self.is_exploding = True
        self.dx = 0
        self.dy = 0
        self.explosion_timer = len(frames) * frame_time
        self.texture_id = texture_id
        self.animation = Animation(frames, frame_time)


    def get_collision_rect(self) -> pygame.Rect:
        """
        Calculates the collision box adapted for rotation and 'wobble'.
        """
        distance_traveled = self.lifetime * self.speed
        wobble = math.sin(distance_traveled * self.wobble_frequency) * 3
        current_x = self.x + (self.nx * wobble)
        current_y = self.y + (self.ny * wobble)
        
        frame_idx = self.animation.get_current_frame()
        current_surf = self.rotated_frames[frame_idx]
        
        return current_surf.get_rect(center=(current_x, current_y))

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

        # PROCEDURAL LIGHTNING VISUALS
        if getattr(self, 'is_electric', False) and not self.is_exploding:
            import random
            # Calculate a dynamic bounding box based on velocity for the sparks
            offset_x = self.dx * 0.04
            offset_y = self.dy * 0.04
            
            start_pos = (render_x - offset_x, render_y - offset_y)
            end_pos = (render_x + offset_x, render_y + offset_y)
            
            # Generate jagged points
            points = [start_pos]
            for _ in range(2):
                mid_x = (start_pos[0] + end_pos[0]) / 2 + random.uniform(-12, 12)
                mid_y = (start_pos[1] + end_pos[1]) / 2 + random.uniform(-12, 12)
                points.append((mid_x, mid_y))
            points.append(end_pos)
            
            # Draw an intense cyan glow (width 3) and a white core (width 1)
            pygame.draw.lines(surface, (0, 255, 255), False, points, 3)
            pygame.draw.lines(surface, (255, 255, 255), False, points, 1)