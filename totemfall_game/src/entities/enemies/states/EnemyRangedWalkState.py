import math
import pygame
from src.entities.BaseEntityState import BaseEntityState

class EnemyRangedWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations['walk']

    def update(self, dt: float) -> None:
        if getattr(self.entity, 'is_spawning', False):
            return
            
        if hasattr(self.entity, 'target'):
            center_x = self.entity.x + (self.entity.width / 2)
            center_y = self.entity.y + (self.entity.height / 2)
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height / 2)
            
            distance = math.hypot(target_center_x - center_x, target_center_y - center_y)
            
            if hasattr(self.entity, 'attack_range') and distance <= self.entity.attack_range:
                if 'attack' in self.entity.state_machine.states:
                    self.entity.state_machine.change('attack')
                    