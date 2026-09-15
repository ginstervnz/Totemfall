import pygame
import math
import settings
from gale.animation import Animation

class ExpOrb:
    def __init__(self, x: float, y: float, xp_value: int):
        self.x = x
        self.y = y
        self.xp_value = xp_value
        self.speed = 200 # Travel speed towards the totem
        self.radius = 10 # Invisible collision radius
        self.active = True
        
        # ANIMATION SETUP
        # Get the total number of frames generated in settings
        total_frames = len(settings.FRAMES.get('xp_orb_frames', [0]))
        
        # Create the animation (0.05 seconds per frame for a fast splash effect)
        frame_list = list(range(total_frames))
        self.anim = Animation(frame_list, 0.05)

    def update(self, dt: float, target_x: float, target_y: float) -> None:
        """Moves the orb directly towards the target and updates animation."""
        # 1. Update movement
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += math.cos(angle) * self.speed * dt
        self.y += math.sin(angle) * self.speed * dt
        
        # 2. Update animation timer
        self.anim.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draws the animated vortex sprite centered on the coordinates."""
        if 'xp_orb' in settings.TEXTURES and 'xp_orb_frames' in settings.FRAMES:
            image = settings.TEXTURES['xp_orb']
            
            # Get the current frame from the animation
            frame_idx = self.anim.get_current_frame()
            frame_rect = settings.FRAMES['xp_orb_frames'][frame_idx]
            
            orb_surface = image.subsurface(frame_rect)
            
            # Offset by half width/height to center the sprite exactly on self.x and self.y
            offset_x = self.x - (frame_rect.width / 2)
            offset_y = self.y - (frame_rect.height / 2)
            
            surface.blit(orb_surface, (offset_x, offset_y))