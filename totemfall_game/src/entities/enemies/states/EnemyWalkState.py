import pygame
from src.entities.BaseEntityState import BaseEntityState

class EnemyWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations['walk']

    def update(self, dt: float) -> None:
        if getattr(self.entity, 'is_spawning', False):
            return
            
        if hasattr(self.entity, 'target'):
            # Combat Hitbox: Full body for detecting if they can attack the target
            enemy_rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
            target_rect = pygame.Rect(self.entity.target.x, self.entity.target.y, self.entity.target.width, self.entity.target.height)
            
            if enemy_rect.colliderect(target_rect):
                if 'attack' in self.entity.state_machine.states:
                    self.entity.state_machine.change('attack')
                    