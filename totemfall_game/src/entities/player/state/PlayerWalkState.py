import pygame
import settings
from src.entities.BaseEntityState import BaseEntityState

class PlayerWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation('walk')

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        
        if any(keys[key] for key in settings.CONTROLS['left']):
            self.entity.x -= self.entity.speed * dt
            self.entity.facing_right = False
        elif any(keys[key] for key in settings.CONTROLS['right']):
            self.entity.x += self.entity.speed * dt
            self.entity.facing_right = True
        else:
            self.state_machine.change('idle')

        margin = 5
        self.entity.x = max(margin, min(self.entity.x, settings.VIRTUAL_WIDTH - self.entity.width - margin))