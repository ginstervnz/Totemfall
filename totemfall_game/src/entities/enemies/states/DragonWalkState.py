import math
import pygame
from src.entities.BaseEntityState import BaseEntityState

class DragonWalkState(BaseEntityState):
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
            
            # Priority 1: Melee Attack if they get too close
            if hasattr(self.entity, 'melee_range') and distance <= self.entity.melee_range:
                if 'attack_melee' in self.entity.state_machine.states:
                    self.entity.state_machine.change('attack_melee')
                    
            # Priority 2: Ranged Attack if further away
            elif hasattr(self.entity, 'attack_range') and distance <= self.entity.attack_range:
                if getattr(self.entity, 'ranged_cooldown_timer', 0) <= 0:
                    self.entity.ranged_cooldown_timer = getattr(self.entity, 'ranged_cooldown_max', 3.0)
                    if 'attack_ranged' in self.entity.state_machine.states:
                        self.entity.state_machine.change('attack_ranged')
                        