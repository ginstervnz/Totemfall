import math
from src.entities.BaseEntityState import BaseEntityState

class EnemyRangedWalkState(BaseEntityState):
    def enter(self) -> None:
        self.entity.current_animation = self.entity.animations['walk']

    def update(self, dt: float) -> None:
        if hasattr(self.entity, 'target'):
            
            center_x = self.entity.x + (self.entity.width / 2)
            center_y = self.entity.y + (self.entity.height / 2)
            target_center_x = self.entity.target.x + (self.entity.target.width / 2)
            target_center_y = self.entity.target.y + (self.entity.target.height / 2)
            
           
            dist_x = target_center_x - center_x
            dist_y = target_center_y - center_y
            distance = math.hypot(dist_x, dist_y)
            
            
            if hasattr(self.entity, 'attack_range') and distance <= self.entity.attack_range:
                if 'attack' in self.entity.state_machine.states:
                    self.entity.state_machine.change('attack')
            else:
        
                angle = math.atan2(dist_y, dist_x)
                self.entity.x += math.cos(angle) * self.entity.speed * dt
                self.entity.y += math.sin(angle) * self.entity.speed * dt
        else:
            self.entity.y += self.entity.speed * dt