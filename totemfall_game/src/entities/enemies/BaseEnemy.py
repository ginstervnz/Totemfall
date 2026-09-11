import pygame

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

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True

    def update(self, dt: float) -> None:
        if self.state_machine:
            self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)

    def render(self, surface: pygame.Surface, texture_id: str, frames_id: str) -> None:
        if not self.current_animation: return
        
        import settings
        image = settings.TEXTURES[texture_id]
        frame_idx = self.current_animation.get_current_frame()
        frame_rect = settings.FRAMES[frames_id][frame_idx]
        
        enemy_surface = image.subsurface(frame_rect)
        surface.blit(enemy_surface, (self.x, self.y))