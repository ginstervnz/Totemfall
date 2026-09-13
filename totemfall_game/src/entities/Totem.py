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

        #Heal
        self.max_hp = 5
        self.hp = self.max_hp
        self.hit_flash_timer = 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)
        self.hit_flash_timer = 0.15

    def update(self, dt: float) -> None:
        self.animation.update(dt)

        #Heal
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt

    def render(self, surface: pygame.Surface) -> None:
        image = settings.TEXTURES['obelisk']
        frame_idx = self.animation.get_current_frame()
        frame_rect = settings.FRAMES['obelisk_frames'][frame_idx]
        
        entity_surface = image.subsurface(frame_rect).copy() 
                
        if self.hit_flash_timer > 0:
            entity_surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
                    
        surface.blit(entity_surface, (self.x, self.y))