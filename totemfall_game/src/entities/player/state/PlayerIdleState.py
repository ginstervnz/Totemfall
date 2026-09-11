import pygame
from src.entities.BaseEntityState import BaseEntityState

class PlayerIdleState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation('idle')

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.state_machine.change('walk')