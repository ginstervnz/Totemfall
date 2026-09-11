import pygame
import settings
from gale.animation import Animation

class Totem:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 38
        self.height = 48
        self.animation = Animation(list(range(14)), 0.15)

    def update(self, dt: float) -> None:
        self.animation.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['obelisk']
        frame_idx = self.animation.get_current_frame()
        frame_rect = settings.FRAMES['obelisk_frames'][frame_idx]
        
        obelisk_surface = image.subsurface(frame_rect)
        surface.blit(obelisk_surface, (self.x, self.y))