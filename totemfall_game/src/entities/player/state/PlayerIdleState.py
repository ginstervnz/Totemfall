import pygame
import settings
from src.entities.BaseEntityState import BaseEntityState

class PlayerIdleState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation('idle')

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        
        list_move = settings.CONTROLS['left'] + settings.CONTROLS['right']
        
        if any(keys[key] for key in list_move):
            self.state_machine.change('walk')