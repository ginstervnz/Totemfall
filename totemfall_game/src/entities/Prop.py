import pygame
import settings

class Prop:
    def __init__(self, x: float, y: float, texture_id: str, frame: int = 0, solid: bool = False):
        self.x = x
        self.y = y
        self.texture_id = texture_id
        self.frame = frame
        self.solid = solid
        
        # It is assumed that the props have the same dimensions as a map block.
        self.width = settings.TILE_SIZE
        self.height = settings.TILE_SIZE

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        texture = settings.TEXTURES[self.texture_id]
        frame_rect = settings.FRAMES[self.texture_id][self.frame]
        
        surface.blit(
            texture,
            (self.x + offset_x, self.y + offset_y),
            frame_rect
        )